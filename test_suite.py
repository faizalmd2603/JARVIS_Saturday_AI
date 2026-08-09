import os
import sys
import unittest
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

class TestJarvisAvengersSystem(unittest.TestCase):

    def test_01_api_router(self):
        from api_router import router
        res = router.generate_completion("Respond with 'ROUTER ONLINE'")
        self.assertIsNotNone(res)
        print(f"\n[PASS] DualAPIRouter Response: {res[:100]}")

    def test_02_friday_agent(self):
        from agents.friday import FridayAgent
        agent = FridayAgent()
        brief = agent.get_daily_brief()
        self.assertEqual(brief["status"], "success")
        
        task_res = agent.add_task("Verify AVENGERS Protocol Initialization")
        self.assertEqual(task_res["status"], "success")
        print(f"\n[PASS] FRIDAY Agent Brief: {brief['brief'][:100]}")

    def test_03_stark_agent(self):
        from agents.stark import StarkAgent
        agent = StarkAgent()
        res = agent.launch_taskbar_app(1)
        self.assertEqual(res["status"], "success")
        print(f"\n[PASS] STARK Agent Taskbar Slot 1 Triggered: {res['message']}")

    def test_04_spectre_agent(self):
        from agents.spectre import SpectreAgent
        agent = SpectreAgent()
        tabs_res = asyncio.run(agent.list_tabs())
        self.assertEqual(tabs_res["status"], "success")
        print(f"\n[PASS] SPECTRE Agent Tab Controller: {tabs_res}")

    def test_05_herald_agent(self):
        from agents.herald import HeraldAgent
        agent = HeraldAgent()
        res = agent.execute("JARVIS voice protocol verified.")
        self.assertEqual(res["status"], "success")
        print(f"\n[PASS] HERALD Voice Agent: {res['message']}")

    def test_06_banner_agent(self):
        from agents.banner import BannerAgent
        agent = BannerAgent()
        design_res = agent.generate_design("Iron Man Arc Reactor Concept", "STARK INDUSTRIES")
        self.assertEqual(design_res["status"], "success")
        self.assertTrue(os.path.exists(design_res["filepath"]))
        print(f"\n[PASS] BANNER Design Agent Created File: {design_res['filepath']}")

    def test_07_hulk_agent(self):
        from agents.hulk import HulkAgent
        agent = HulkAgent()
        health = agent.system_health_check()
        self.assertEqual(health["status"], "success")
        print(f"\n[PASS] HULK Offline Agent Health Check: {health['message']}")

    def test_08_main_orchestrator(self):
        from main_orchestrator import orchestrator
        async def run_orch():
            steps = []
            async for step in orchestrator.route_and_execute_stream("Generate Iron Man design poster"):
                steps.append(step)
            return steps

        steps = asyncio.run(run_orch())
        self.assertGreater(len(steps), 0)
        self.assertEqual(steps[-1]["event"], "completed")
        print(f"\n[PASS] JARVIS Main Orchestrator Stream Completed with {len(steps)} steps.")

if __name__ == "__main__":
    unittest.main()
