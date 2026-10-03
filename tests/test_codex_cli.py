"""CLI selection and the shared auth/version/exec boundary."""
import json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from motif_direct import resolve_codex_cli,backend_config,model_call

class CodexCliTests(unittest.TestCase):
 def test_desktop_runtime_precedes_old_path_cli(self):
  with patch.dict(os.environ,{},clear=True),patch('pathlib.Path.is_file',return_value=True),patch('os.access',return_value=True),patch('motif_direct.shutil.which',return_value='/old/codex') as lookup:
   selected=resolve_codex_cli()
  self.assertEqual(selected['cli_selection'],'desktop-bundled CLI')
  self.assertTrue(selected['cli_path'].endswith('/codex-cli/CodexCLI.app/Contents/MacOS/codex'))
  lookup.assert_not_called()
 def test_invalid_explicit_override_cannot_fall_back(self):
  with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'MOTIF_CODEX_CLI':str(Path(d)/'missing')}),patch('motif_direct.shutil.which') as lookup:
   with self.assertRaisesRegex(ValueError,'executable file'):resolve_codex_cli()
   lookup.assert_not_called()
 def test_path_is_recorded_when_desktop_bundle_unavailable(self):
  with patch.dict(os.environ,{},clear=True),patch('pathlib.Path.is_file',return_value=False),patch('motif_direct.shutil.which',return_value='/usr/local/bin/codex'):
   self.assertEqual(resolve_codex_cli(),{'cli_path':'/usr/local/bin/codex','cli_selection':'PATH (desktop bundle unavailable)'})
 def test_selected_binary_handles_login_version_and_structured_exec(self):
  response={'pass':True,'issues':[],'message_preserved':True,'outcome_preserved':True,'evidence_before_labels':True,'ending_delivered':True,'notes':'UNIT ONLY','audience_narration':True}
  with tempfile.TemporaryDirectory() as d:
   folder=Path(d);cli=folder/'selected cli';ledger=folder/'calls.jsonl'
   cli.write_text('#!'+sys.executable+'\nimport sys,json\nwith open('+repr(str(ledger))+',"a") as f:f.write(json.dumps(sys.argv)+"\\n")\nif sys.argv[1:]==["login","status"]:print("Logged in using fixture")\nelif sys.argv[1:]==["--version"]:print("codex-cli fixture-selected")\nelif sys.argv[1]=="exec":\n sys.stdin.read()\n with open(sys.argv[sys.argv.index("-o")+1],"w") as f:json.dump('+repr(response)+',f)\n print(json.dumps({"type":"item.completed","item":{"type":"agent_message","text":"unit response"}}))\nelse:sys.exit(2)\n');cli.chmod(0o755)
   with patch.dict(os.environ,{'MOTIF_CODEX_CLI':str(cli),'MOTIF_PLANNER_MODEL':'gpt-6.1-sol'}):
    config=backend_config();result=model_call(Path(os.path.relpath(folder)),'probe','Data only, no tools.','schemas/planning-review.schema.json',config)
   calls=[json.loads(x) for x in ledger.read_text().splitlines()]
   self.assertEqual([x[1] for x in calls],['login','--version','exec'])
   self.assertTrue(all(Path(x[0]).resolve()==cli.resolve() for x in calls));self.assertEqual(result,response)
   record=json.loads((folder/'probe-invocation.json').read_text())
   self.assertEqual(record['argv'][0],config['cli_path']);self.assertEqual(config['cli_version'],'codex-cli fixture-selected')
   self.assertTrue(Path(record['argv'][record['argv'].index('-o')+1]).is_absolute())
   self.assertEqual(record['requested_model'],'gpt-6.1-sol');self.assertFalse(record['model_fallback_used'])
 def test_missing_recorded_binary_does_not_switch_cli(self):
  with tempfile.TemporaryDirectory() as d,patch('motif_direct.resolve_codex_cli') as resolver:
   folder=Path(d)
   with self.assertRaisesRegex(ValueError,'recorded Codex CLI'):model_call(folder,'probe','unit','schemas/planning-review.schema.json',{'cli_path':str(folder/'missing')})
   resolver.assert_not_called()
if __name__=='__main__':unittest.main()
