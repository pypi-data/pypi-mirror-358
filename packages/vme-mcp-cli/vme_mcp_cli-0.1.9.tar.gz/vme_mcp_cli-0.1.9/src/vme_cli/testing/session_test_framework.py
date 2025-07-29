"""
Session Testing Framework for VME Chat Client
Automated testing of user workflows based on session log analysis
"""

import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TestResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    TIMEOUT = "timeout"
    ERROR = "error"

class TestCategory(Enum):
    TOOL_EXECUTION = "tool_execution"
    RESPONSE_TIME = "response_time"
    USER_EXPERIENCE = "user_experience"
    INTENT_CLASSIFICATION = "intent_classification"
    ERROR_HANDLING = "error_handling"
    WORKFLOW_COMPLETION = "workflow_completion"

@dataclass
class TestCase:
    """Individual test case definition"""
    id: str
    name: str
    description: str
    category: TestCategory
    user_input: str
    expected_tools: List[str] = field(default_factory=list)
    expected_intent: Optional[str] = None
    max_response_time_ms: Optional[float] = None
    should_complete_workflow: bool = False
    expected_error: Optional[str] = None
    timeout_seconds: int = 30

@dataclass
class TestExecution:
    """Results of a test execution"""
    test_case: TestCase
    result: TestResult
    actual_tools_called: List[str] = field(default_factory=list)
    actual_intent: Optional[str] = None
    actual_response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    session_data: Optional[Dict] = None
    execution_time: float = 0.0

class SessionTestFramework:
    """Framework for testing session improvements"""
    
    def __init__(self, test_cases_file: str = "test_cases.json"):
        self.test_cases_file = test_cases_file
        self.test_cases = []
        self.results = []
        self.load_test_cases()
    
    def load_test_cases(self):
        """Load test cases from file or create default ones"""
        test_cases_path = Path(self.test_cases_file)
        
        if test_cases_path.exists():
            try:
                with open(test_cases_path, 'r') as f:
                    data = json.load(f)
                    self.test_cases = [self._dict_to_test_case(tc) for tc in data]
                logger.info(f"📝 Loaded {len(self.test_cases)} test cases from {self.test_cases_file}")
            except Exception as e:
                logger.error(f"❌ Failed to load test cases: {e}")
                self._create_default_test_cases()
        else:
            self._create_default_test_cases()
    
    def _create_default_test_cases(self):
        """Create default test cases based on problematic session"""
        self.test_cases = [
            # Tool Execution Tests
            TestCase(
                id="vm_list_execution",
                name="VM List Tool Execution",
                description="Test that asking for VMs actually calls the right tools",
                category=TestCategory.TOOL_EXECUTION,
                user_input="Any VM instances running?",
                expected_tools=["vme_compute_Get_All_Instances"],
                max_response_time_ms=3000
            ),
            
            TestCase(
                id="vm_creation_tools",
                name="VM Creation Tool Discovery",
                description="Test that VM creation triggers proper tool discovery",
                category=TestCategory.TOOL_EXECUTION,
                user_input="I'd like to create a VM",
                expected_tools=["vme_virtual_images_Get_All_Virtual_Images", "vme_service_plans_Get_All_Service_Plans"],
                max_response_time_ms=4000
            ),
            
            TestCase(
                id="vm_creation_with_specs",
                name="VM Creation with Specifications",
                description="Test complete VM creation workflow",
                category=TestCategory.WORKFLOW_COMPLETION,
                user_input="Create a Rocky Linux VM with 8GB memory",
                expected_tools=["resolve_image_name", "resolve_service_plan_name", "vme_compute_Create_an_Instance"],
                should_complete_workflow=True,
                max_response_time_ms=8000
            ),
            
            # Intent Classification Tests
            TestCase(
                id="vm_creation_intent",
                name="VM Creation Intent Classification",
                description="Test that VM creation requests are classified correctly",
                category=TestCategory.INTENT_CLASSIFICATION,
                user_input="I'd like to create a VM",
                expected_intent="resource_creation"
            ),
            
            TestCase(
                id="vm_specs_intent",
                name="VM Specification Intent Classification", 
                description="Test that VM specs are classified as resource creation",
                category=TestCategory.INTENT_CLASSIFICATION,
                user_input="Any rocky will do and just go 8 gig in memory",
                expected_intent="resource_creation"  # Should be this, not general_inquiry
            ),
            
            TestCase(
                id="vm_list_intent",
                name="VM List Intent Classification",
                description="Test that VM listing requests are classified correctly",
                category=TestCategory.INTENT_CLASSIFICATION,
                user_input="Any VM instances running?",
                expected_intent="information_retrieval"
            ),
            
            # Response Time Tests
            TestCase(
                id="fast_vm_list",
                name="Fast VM List Response",
                description="Test that VM listing is fast",
                category=TestCategory.RESPONSE_TIME,
                user_input="List all VMs",
                max_response_time_ms=2000
            ),
            
            TestCase(
                id="fast_simple_query",
                name="Fast Simple Query Response",
                description="Test that simple queries are very fast",
                category=TestCategory.RESPONSE_TIME,
                user_input="Hello",
                max_response_time_ms=1500
            ),
            
            # Error Handling Tests
            TestCase(
                id="empty_message_handling",
                name="Empty Message Error Handling",
                description="Test that empty messages are handled gracefully",
                category=TestCategory.ERROR_HANDLING,
                user_input="",
                expected_error=None,  # Should NOT produce an error
                max_response_time_ms=100
            ),
            
            TestCase(
                id="minimal_message_handling", 
                name="Minimal Message Handling",
                description="Test that minimal messages are handled gracefully",
                category=TestCategory.ERROR_HANDLING,
                user_input=".",
                expected_error=None,
                max_response_time_ms=1000
            ),
            
            # User Experience Tests
            TestCase(
                id="tool_execution_clarity",
                name="Tool Execution Clarity",
                description="Test that tools are executed, not just mentioned",
                category=TestCategory.USER_EXPERIENCE,
                user_input="Show me my virtual machines",
                expected_tools=["vme_compute_Get_All_Instances"],
                max_response_time_ms=3000
            ),
            
            TestCase(
                id="no_repeated_discovery",
                name="No Repeated Discovery",
                description="Test that discovery tools aren't called repeatedly",
                category=TestCategory.USER_EXPERIENCE,
                user_input="What VMs do I have?",
                # Should NOT call discover_compute_infrastructure if already called
                max_response_time_ms=2500
            ),
        ]
        
        # Save default test cases
        self.save_test_cases()
        logger.info(f"📝 Created {len(self.test_cases)} default test cases")
    
    def save_test_cases(self):
        """Save test cases to file"""
        try:
            test_cases_data = [self._test_case_to_dict(tc) for tc in self.test_cases]
            with open(self.test_cases_file, 'w') as f:
                json.dump(test_cases_data, f, indent=2)
            logger.info(f"💾 Saved test cases to {self.test_cases_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save test cases: {e}")
    
    def _test_case_to_dict(self, test_case: TestCase) -> Dict:
        """Convert test case to dictionary"""
        return {
            "id": test_case.id,
            "name": test_case.name,
            "description": test_case.description,
            "category": test_case.category.value,
            "user_input": test_case.user_input,
            "expected_tools": test_case.expected_tools,
            "expected_intent": test_case.expected_intent,
            "max_response_time_ms": test_case.max_response_time_ms,
            "should_complete_workflow": test_case.should_complete_workflow,
            "expected_error": test_case.expected_error,
            "timeout_seconds": test_case.timeout_seconds
        }
    
    def _dict_to_test_case(self, data: Dict) -> TestCase:
        """Convert dictionary to test case"""
        return TestCase(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            category=TestCategory(data["category"]),
            user_input=data["user_input"],
            expected_tools=data.get("expected_tools", []),
            expected_intent=data.get("expected_intent"),
            max_response_time_ms=data.get("max_response_time_ms"),
            should_complete_workflow=data.get("should_complete_workflow", False),
            expected_error=data.get("expected_error"),
            timeout_seconds=data.get("timeout_seconds", 30)
        )
    
    async def run_test_case(self, test_case: TestCase, session_logger) -> TestExecution:
        """Run a single test case"""
        logger.info(f"🧪 Running test: {test_case.name}")
        start_time = time.time()
        
        try:
            # Start fresh session for this test
            session_logger.current_session.messages.clear()
            session_logger.current_session.intent_analysis.clear()
            
            # Log the user message
            session_logger.log_user_message(test_case.user_input)
            
            # TODO: This would integrate with actual chat app
            # For now, we'll simulate the test execution
            
            execution_time = time.time() - start_time
            
            # Analyze session data
            session_data = session_logger.current_session
            
            # Extract results
            actual_tools_called = []
            actual_intent = None
            actual_response_time_ms = None
            
            # Get tool calls from messages
            for message in session_data.messages:
                actual_tools_called.extend([tc.tool_name for tc in message.tool_calls])
                if message.response_time_ms:
                    actual_response_time_ms = message.response_time_ms
            
            # Get intent from analysis
            if session_data.intent_analysis:
                actual_intent = session_data.intent_analysis[-1].inferred_intent
            
            # Determine test result
            result = self._evaluate_test_result(test_case, actual_tools_called, actual_intent, actual_response_time_ms)
            
            return TestExecution(
                test_case=test_case,
                result=result,
                actual_tools_called=actual_tools_called,
                actual_intent=actual_intent,
                actual_response_time_ms=actual_response_time_ms,
                execution_time=execution_time,
                session_data=session_data.__dict__ if hasattr(session_data, '__dict__') else str(session_data)
            )
            
        except asyncio.TimeoutError:
            return TestExecution(
                test_case=test_case,
                result=TestResult.TIMEOUT,
                execution_time=time.time() - start_time,
                error_message=f"Test timed out after {test_case.timeout_seconds} seconds"
            )
            
        except Exception as e:
            return TestExecution(
                test_case=test_case,
                result=TestResult.ERROR,
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _evaluate_test_result(self, test_case: TestCase, actual_tools: List[str], 
                            actual_intent: str, actual_response_time: float) -> TestResult:
        """Evaluate whether test case passed or failed"""
        
        # Check expected tools
        if test_case.expected_tools:
            missing_tools = set(test_case.expected_tools) - set(actual_tools)
            if missing_tools:
                logger.warning(f"❌ Missing expected tools: {missing_tools}")
                return TestResult.FAIL
        
        # Check expected intent
        if test_case.expected_intent and actual_intent != test_case.expected_intent:
            logger.warning(f"❌ Intent mismatch: expected {test_case.expected_intent}, got {actual_intent}")
            return TestResult.FAIL
        
        # Check response time
        if test_case.max_response_time_ms and actual_response_time:
            if actual_response_time > test_case.max_response_time_ms:
                logger.warning(f"❌ Response too slow: {actual_response_time:.0f}ms > {test_case.max_response_time_ms:.0f}ms")
                return TestResult.FAIL
        
        # Check error expectations
        if test_case.expected_error is None:
            # Should not have any errors - check session for errors
            # This would need to be implemented based on actual session structure
            pass
        
        return TestResult.PASS
    
    async def run_all_tests(self, session_logger) -> Dict[str, Any]:
        """Run all test cases and return results"""
        logger.info(f"🚀 Running {len(self.test_cases)} test cases...")
        
        self.results = []
        start_time = time.time()
        
        for test_case in self.test_cases:
            try:
                execution = await asyncio.wait_for(
                    self.run_test_case(test_case, session_logger),
                    timeout=test_case.timeout_seconds
                )
                self.results.append(execution)
                
                # Log result
                status_emoji = "✅" if execution.result == TestResult.PASS else "❌"
                logger.info(f"{status_emoji} {test_case.name}: {execution.result.value}")
                
            except Exception as e:
                logger.error(f"❌ Test framework error for {test_case.name}: {e}")
                self.results.append(TestExecution(
                    test_case=test_case,
                    result=TestResult.ERROR,
                    error_message=str(e)
                ))
        
        total_time = time.time() - start_time
        
        # Generate summary
        summary = self._generate_test_summary(total_time)
        
        # Save results
        self._save_test_results(summary)
        
        return summary
    
    def _generate_test_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate test execution summary"""
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.result == TestResult.PASS])
        failed = len([r for r in self.results if r.result == TestResult.FAIL])
        errors = len([r for r in self.results if r.result == TestResult.ERROR])
        timeouts = len([r for r in self.results if r.result == TestResult.TIMEOUT])
        
        # Category breakdown
        category_results = {}
        for category in TestCategory:
            category_tests = [r for r in self.results if r.test_case.category == category]
            category_passed = len([r for r in category_tests if r.result == TestResult.PASS])
            category_results[category.value] = {
                "total": len(category_tests),
                "passed": category_passed,
                "pass_rate": category_passed / len(category_tests) if category_tests else 0
            }
        
        summary = {
            "timestamp": time.time(),
            "total_execution_time": total_time,
            "overall": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "timeouts": timeouts,
                "pass_rate": passed / total_tests if total_tests > 0 else 0
            },
            "by_category": category_results,
            "failed_tests": [
                {
                    "id": r.test_case.id,
                    "name": r.test_case.name,
                    "result": r.result.value,
                    "error": r.error_message
                }
                for r in self.results if r.result != TestResult.PASS
            ],
            "detailed_results": [
                {
                    "test_id": r.test_case.id,
                    "name": r.test_case.name,
                    "category": r.test_case.category.value,
                    "result": r.result.value,
                    "execution_time": r.execution_time,
                    "actual_tools": r.actual_tools_called,
                    "actual_intent": r.actual_intent,
                    "actual_response_time_ms": r.actual_response_time_ms,
                    "error": r.error_message
                }
                for r in self.results
            ]
        }
        
        return summary
    
    def _save_test_results(self, summary: Dict[str, Any]):
        """Save test results to file"""
        results_file = f"test_results_{int(time.time())}.json"
        try:
            with open(results_file, 'w') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"💾 Test results saved to {results_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save test results: {e}")
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print human-readable test summary"""
        overall = summary["overall"]
        
        print("\n" + "="*60)
        print("🧪 SESSION TEST FRAMEWORK RESULTS")
        print("="*60)
        
        print(f"\n📊 Overall Results:")
        print(f"  Total Tests: {overall['total_tests']}")
        print(f"  Passed: {overall['passed']} ✅")
        print(f"  Failed: {overall['failed']} ❌") 
        print(f"  Errors: {overall['errors']} 💥")
        print(f"  Timeouts: {overall['timeouts']} ⏰")
        print(f"  Pass Rate: {overall['pass_rate']:.1%}")
        
        print(f"\n📈 Results by Category:")
        for category, results in summary["by_category"].items():
            if results["total"] > 0:
                print(f"  {category.replace('_', ' ').title()}: {results['passed']}/{results['total']} ({results['pass_rate']:.1%})")
        
        if summary["failed_tests"]:
            print(f"\n❌ Failed Tests:")
            for test in summary["failed_tests"]:
                print(f"  - {test['name']}: {test['result']}")
                if test.get("error"):
                    print(f"    Error: {test['error']}")
        
        print(f"\n⏱️  Total Execution Time: {summary['total_execution_time']:.2f} seconds")
        print("="*60)

# Performance Benchmark Tests
class PerformanceBenchmark:
    """Specific performance benchmarks based on session analysis"""
    
    @staticmethod
    def create_performance_test_cases() -> List[TestCase]:
        """Create performance-focused test cases"""
        return [
            TestCase(
                id="response_time_baseline",
                name="Response Time Baseline",
                description="Baseline response time for simple queries",
                category=TestCategory.RESPONSE_TIME,
                user_input="Hello",
                max_response_time_ms=1000  # Much faster than 3.4s observed
            ),
            
            TestCase(
                id="vm_list_performance",
                name="VM List Performance",
                description="VM listing should be under 2 seconds",
                category=TestCategory.RESPONSE_TIME,
                user_input="List my VMs",
                max_response_time_ms=2000  # vs 4.6s average observed
            ),
            
            TestCase(
                id="tool_discovery_cache",
                name="Tool Discovery Caching",
                description="Second discovery call should be much faster",
                category=TestCategory.RESPONSE_TIME,
                user_input="What infrastructure do I have?",
                max_response_time_ms=500  # Should use cache
            ),
        ]

# Regression Tests
class RegressionTests:
    """Tests to prevent regression of fixed issues"""
    
    @staticmethod
    def create_regression_test_cases() -> List[TestCase]:
        """Create regression test cases for known fixes"""
        return [
            TestCase(
                id="no_anthropic_400_error",
                name="No Anthropic 400 Error",
                description="Empty messages should not cause API errors",
                category=TestCategory.ERROR_HANDLING,
                user_input="",
                expected_error=None
            ),
            
            TestCase(
                id="actual_tool_execution",
                name="Actual Tool Execution",
                description="Tools should be executed, not just mentioned",
                category=TestCategory.TOOL_EXECUTION,
                user_input="Show me running VMs",
                expected_tools=["vme_compute_Get_All_Instances"]
            ),
        ]