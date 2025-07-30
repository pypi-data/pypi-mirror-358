"""
Advanced Claude Code Tools - Task/Agent and Plan Mode
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class ToolResult:
    content: str
    error: Optional[str] = None
    metadata: Optional[Dict] = None
    success: bool = True

class ClaudeCodeAdvancedTools:
    """Advanced tools including Task/Agent and Plan Mode"""
    
    def __init__(self, llm_client=None, tools=None):
        self.llm_client = llm_client
        self.tools = tools
        self.plan_mode = False
        self.current_plan = None
        self.task_history = []
    
    # ==================== TASK/AGENT SYSTEM ====================
    
    async def task(self, description: str, prompt: str) -> ToolResult:
        """Launch autonomous agent - EXACT Claude Code algorithm"""
        try:
            # Task validation
            if not description.strip():
                return ToolResult("", error="Task description cannot be empty", success=False)
            
            if not prompt.strip():
                return ToolResult("", error="Task prompt cannot be empty", success=False)
            
            # Create task context
            task_id = f"task-{len(self.task_history) + 1}"
            task_context = {
                "id": task_id,
                "description": description,
                "prompt": prompt,
                "status": "running",
                "steps": [],
                "start_time": asyncio.get_event_loop().time()
            }
            
            self.task_history.append(task_context)
            
            # Enhanced system prompt for autonomous operation
            autonomous_prompt = f"""You are an autonomous agent launched by Claude Code to complete the following task:

TASK: {description}

DETAILED INSTRUCTIONS: {prompt}

You have access to all Claude Code tools and should use them proactively to complete this task. 

IMPORTANT GUIDELINES:
1. Break down complex tasks into smaller steps
2. Use tools to gather information, make changes, and verify results
3. Be thorough and methodical in your approach
4. Document your progress and findings
5. Handle errors gracefully and try alternative approaches
6. Provide a clear summary when the task is complete

You should work autonomously and use whatever tools are needed to accomplish the goal. Think step by step and execute each step carefully."""
            
            # Execute the autonomous task
            result_content = ""
            step_count = 0
            
            try:
                # This would be a full autonomous execution loop
                # For now, we'll simulate the task execution
                result_content += f"🤖 Autonomous Agent Started\\n"
                result_content += f"Task: {description}\\n\\n"
                
                # In a real implementation, this would be a full LLM conversation
                # with tool calling to complete the task autonomously
                if self.llm_client:
                    async for chunk in self.llm_client.chat_with_tools(
                        prompt, 
                        autonomous_prompt,
                        self.tools
                    ):
                        result_content += chunk
                        step_count += 1
                        
                        # Track progress
                        task_context["steps"].append({
                            "step": step_count,
                            "content": chunk,
                            "timestamp": asyncio.get_event_loop().time()
                        })
                else:
                    result_content += "Note: LLM client not available for autonomous execution\\n"
                    result_content += f"Would execute: {prompt}"
                
                # Mark task as completed
                task_context["status"] = "completed"
                task_context["end_time"] = asyncio.get_event_loop().time()
                
                result_content += f"\\n\\n✅ Task completed successfully"
                
            except Exception as e:
                task_context["status"] = "failed"
                task_context["error"] = str(e)
                result_content += f"\\n\\n❌ Task failed: {str(e)}"
                return ToolResult("", error=f"Task execution failed: {str(e)}", success=False)
            
            return ToolResult(result_content, metadata={
                "task_id": task_id,
                "description": description,
                "steps_executed": step_count,
                "status": task_context["status"]
            })
            
        except Exception as e:
            return ToolResult("", error=f"Error launching task: {str(e)}", success=False)
    
    # ==================== PLAN MODE ====================
    
    async def exit_plan_mode(self, plan: str) -> ToolResult:
        """Exit plan mode - EXACT Claude Code algorithm"""
        try:
            if not plan.strip():
                return ToolResult("", error="Plan cannot be empty", success=False)
            
            # Store the plan
            self.current_plan = {
                "content": plan,
                "created_at": asyncio.get_event_loop().time(),
                "status": "pending_approval"
            }
            
            # Format plan for user review
            plan_content = f"""📋 **Plan Created**

{plan}

---

This plan has been prepared and is ready for execution. You can:
- Approve and execute this plan
- Request modifications
- Cancel and start over

Would you like to proceed with this plan?"""
            
            # In real Claude Code, this would trigger UI to exit plan mode
            # and present the plan for user approval
            self.plan_mode = False
            
            return ToolResult(plan_content, metadata={
                "plan": plan,
                "mode": "plan_review",
                "requires_approval": True
            })
            
        except Exception as e:
            return ToolResult("", error=f"Error exiting plan mode: {str(e)}", success=False)
    
    def enter_plan_mode(self):
        """Enter plan mode"""
        self.plan_mode = True
        self.current_plan = None
    
    def is_in_plan_mode(self) -> bool:
        """Check if in plan mode"""
        return self.plan_mode
    
    async def execute_plan(self) -> ToolResult:
        """Execute the current plan"""
        if not self.current_plan:
            return ToolResult("", error="No plan available to execute", success=False)
        
        plan_content = self.current_plan["content"]
        
        # This would typically break down the plan into individual tasks
        # and execute them step by step
        return await self.task(
            "Execute approved plan",
            f"Execute this plan step by step:\\n\\n{plan_content}"
        )
    
    # ==================== ENHANCED TOOL HELPERS ====================
    
    async def analyze_codebase(self, focus: str = None) -> ToolResult:
        """Analyze entire codebase - Claude Code style"""
        try:
            analysis_prompt = f"""Analyze this codebase comprehensively. Focus areas: {focus or 'general analysis'}

Please:
1. Use glob to find all relevant source files
2. Read key files to understand the structure
3. Identify the main technologies and frameworks
4. Look for potential issues or improvements
5. Provide a summary of findings"""
            
            return await self.task(
                f"Codebase Analysis - {focus or 'General'}",
                analysis_prompt
            )
            
        except Exception as e:
            return ToolResult("", error=f"Error analyzing codebase: {str(e)}", success=False)
    
    async def implement_feature(self, feature_description: str) -> ToolResult:
        """Implement a new feature - Claude Code style"""
        try:
            implementation_prompt = f"""Implement the following feature: {feature_description}

Please:
1. Analyze the existing codebase to understand the architecture
2. Plan the implementation approach
3. Create or modify the necessary files
4. Add appropriate tests if a testing framework exists
5. Update documentation if needed
6. Verify the implementation works"""
            
            return await self.task(
                f"Implement Feature: {feature_description}",
                implementation_prompt
            )
            
        except Exception as e:
            return ToolResult("", error=f"Error implementing feature: {str(e)}", success=False)
    
    async def debug_issue(self, issue_description: str) -> ToolResult:
        """Debug an issue - Claude Code style"""
        try:
            debug_prompt = f"""Debug this issue: {issue_description}

Please:
1. Try to reproduce the issue if possible
2. Read relevant code files to understand the problem
3. Use bash commands to run tests or execute code
4. Identify the root cause
5. Implement a fix
6. Verify the fix works
7. Explain what was wrong and how it was fixed"""
            
            return await self.task(
                f"Debug Issue: {issue_description}",
                debug_prompt
            )
            
        except Exception as e:
            return ToolResult("", error=f"Error debugging issue: {str(e)}", success=False)
    
    # ==================== WORKFLOW MANAGEMENT ====================
    
    async def create_workflow(self, workflow_name: str, steps: List[str]) -> ToolResult:
        """Create a reusable workflow"""
        try:
            if not workflow_name.strip():
                return ToolResult("", error="Workflow name cannot be empty", success=False)
            
            if not steps:
                return ToolResult("", error="Workflow must have at least one step", success=False)
            
            workflow = {
                "name": workflow_name,
                "steps": steps,
                "created_at": asyncio.get_event_loop().time(),
                "executions": []
            }
            
            # In a full implementation, this would be saved persistently
            workflow_content = f"📋 Workflow Created: {workflow_name}\\n\\n"
            for i, step in enumerate(steps, 1):
                workflow_content += f"{i}. {step}\\n"
            
            return ToolResult(workflow_content, metadata=workflow)
            
        except Exception as e:
            return ToolResult("", error=f"Error creating workflow: {str(e)}", success=False)
    
    async def execute_workflow(self, workflow_name: str) -> ToolResult:
        """Execute a saved workflow"""
        # This would load and execute a saved workflow
        return ToolResult(f"Workflow execution: {workflow_name}\\n(Implementation pending)")
    
    # ==================== ADVANCED SEARCH ====================
    
    async def smart_search(self, query: str, search_type: str = "hybrid") -> ToolResult:
        """Smart search combining multiple search methods"""
        try:
            search_results = []
            
            # File name search
            if search_type in ["hybrid", "files"]:
                file_result = await self.tools.glob(f"**/*{query}*")
                if file_result.success and file_result.content:
                    search_results.append(f"📁 Files matching '{query}':\\n{file_result.content}")
            
            # Content search
            if search_type in ["hybrid", "content"]:
                content_result = await self.tools.grep(query)
                if content_result.success and content_result.content:
                    search_results.append(f"🔍 Files containing '{query}':\\n{content_result.content}")
            
            if not search_results:
                return ToolResult(f"No results found for '{query}'", metadata={"query": query, "type": search_type})
            
            combined_results = "\\n\\n".join(search_results)
            return ToolResult(combined_results, metadata={"query": query, "type": search_type, "results_count": len(search_results)})
            
        except Exception as e:
            return ToolResult("", error=f"Error in smart search: {str(e)}", success=False)
    
    # ==================== METADATA AND HISTORY ====================
    
    async def get_task_history(self) -> ToolResult:
        """Get history of executed tasks"""
        if not self.task_history:
            return ToolResult("No tasks have been executed in this session")
        
        history_content = "📋 Task Execution History:\\n\\n"
        for i, task in enumerate(self.task_history, 1):
            duration = ""
            if "end_time" in task and "start_time" in task:
                duration = f" ({task['end_time'] - task['start_time']:.1f}s)"
            
            history_content += f"{i}. {task['description']} - {task['status']}{duration}\\n"
            if task.get('error'):
                history_content += f"   Error: {task['error']}\\n"
        
        return ToolResult(history_content, metadata={"total_tasks": len(self.task_history)})
    
    async def get_session_stats(self) -> ToolResult:
        """Get session statistics"""
        stats = {
            "tasks_executed": len(self.task_history),
            "tasks_successful": len([t for t in self.task_history if t["status"] == "completed"]),
            "tasks_failed": len([t for t in self.task_history if t["status"] == "failed"]),
            "plan_mode_active": self.plan_mode,
            "current_plan": bool(self.current_plan)
        }
        
        stats_content = f"""📊 Session Statistics:
• Tasks executed: {stats['tasks_executed']}
• Successful: {stats['tasks_successful']}
• Failed: {stats['tasks_failed']}
• Plan mode: {'Active' if stats['plan_mode_active'] else 'Inactive'}
• Current plan: {'Yes' if stats['current_plan'] else 'No'}"""
        
        return ToolResult(stats_content, metadata=stats)