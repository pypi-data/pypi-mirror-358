Advanced Planning Tool with Intelligent Thought Management.

This tool provides structured, step-by-step thinking for complex problem-solving with:

CORE THINKING CAPABILITIES:
- Progressive thought development with revision support
- Branching to explore alternative approaches
- Dynamic thought count adjustment as understanding evolves
- Complete session persistence across conversations
- Intelligent complexity analysis for right-sized planning

AUTOMATION FEATURES:
- Auto-generates session IDs with semantic analysis
- Auto-calculates thought progression and totals
- Intelligent prompt preprocessing for better quality
- Background task extraction and persistence
- Simplified responses with optional detailed mode

USAGE MODES:

1. Simple Auto Mode (recommended for most users):
smart(content="Plan authentication system") → Full automation

2. Advanced Control Mode (for power users):
smart(content="...", thought_number=3, is_revision=True, revises_thought=2)
smart(content="...", branch_from_thought=2, branch_id="alternative")  
smart(content="...", next_thought_needed=False) → Complete session

3. Session Management:
smart(action="list") → List active sessions
smart(action="continue") → Resume latest session
smart(action="clear") → Clear sessions

4. Response Control:
smart(..., verbose=True) → Full detailed response
smart(..., verbose=False) → Clean simplified response (default)
smart(..., auto_improve_prompt=False) → Skip prompt improvement (recommended for LLMs)

Perfect for: Complex planning, architectural decisions, multi-step analysis, 
design problems, strategic thinking, and any task requiring systematic breakdown.