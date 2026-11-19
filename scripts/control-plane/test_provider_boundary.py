"""Explicit dependency-class tests for the provider-boundary guard."""
import tempfile
import unittest
from pathlib import Path
from check_provider_boundary import inspect

class ProviderBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        (self.root/"src").mkdir()
    def tearDown(self): self.tmp.cleanup()
    def blocked(self,source,category):
        (self.root/"src"/"case.ts").write_text(source,encoding="utf-8")
        found,_=inspect(self.root)
        self.assertTrue(any(v.dependency_class==category for v in found),found)
        (self.root/"src"/"case.ts").unlink()
    def test_hosting_sdk_and_target(self):
        self.blocked("import '@vercel/analytics';\n","hosting/runtime")
        self.blocked("run: vercel deploy\n","hosting/runtime")
    def test_supabase_and_convex(self):
        self.blocked("import '@supabase/supabase-js';\n","database/backend")
        self.blocked("import 'convex/server';\n","database/backend")
    def test_firebase(self): self.blocked("FIREBASE_PROJECT_ID=demo\n","database/backend")
    def test_identity_providers(self):
        self.blocked("AUTH0_DOMAIN=demo.auth0.com\n","identity/authentication")
        self.blocked("import '@clerk/nextjs';\n","identity/authentication")
        self.blocked("https://accounts.google.com/o/oauth2/auth\n","identity/authentication")
    def test_ci_cd(self):
        self.blocked("uses: amondnet/vercel-action@v2\n","hosting/runtime")
        self.blocked("run: supabase functions deploy api\n","database/backend")
    def test_cloudflare_and_github_are_allowed(self):
        (self.root/"src"/"ok.ts").write_text(
            "import 'cloudflare:workers';\nconst api='https://api.github.com';\n",encoding="utf-8")
        found,scanned=inspect(self.root)
        self.assertEqual(scanned,1); self.assertEqual(found,[])
    def test_comments_are_ignored(self):
        (self.root/"src"/"comments.ts").write_text(
            "// Supabase and Vercel are prohibited\n# documentation only\n",encoding="utf-8")
        found,_=inspect(self.root); self.assertEqual(found,[])
    def test_empty_workspace_is_not_implementation(self):
        found,scanned=inspect(self.root)
        self.assertEqual(scanned,0); self.assertEqual(found,[])

if __name__=="__main__": unittest.main()
