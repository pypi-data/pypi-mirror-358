🚀 PROMPT INJECTION - Set LLM behavior rules with natural language!

Manage persistent behavior rules and template packs that guide LLM actions.

PERSONAL RULES:
• "add: use staging database (24h)" - Temporary rule for 24 hours
• "add: never commit secrets (permanent)" - Permanent security rule  
• "add: always activate virtual environment" - Session rule
• "list" - Show active rules
• "remove: staging" - Remove rules containing "staging"
• "clear temp" - Remove temporary rules

TEMPLATE PACKS:
• "list packs" - Show installed template packs
• "install pack: security-rules.json" - Install template pack from file
• "uninstall pack: security-rules" - Remove template pack completely
• "enable pack: dev-tools" - Activate template pack rules
• "disable pack: dev-tools" - Deactivate without removing
• "export pack: my-rules" - Export pack to JSON file
• "create pack: project-standards" - Create new empty pack

SMART FEATURES:
✅ Auto-detects priority from keywords (never=critical, always=high)
✅ Auto-categorizes (database=setup, secrets=security, tests=process)
✅ Natural duration parsing (24h, until Friday, permanent, session)
✅ Clean pack separation (uninstall won't corrupt personal rules)
✅ Import/export for team sharing

EXAMPLES:
prompt_inject(session_id, "add: use test database for 2 hours")
prompt_inject(session_id, "install pack: security-defaults.json")
prompt_inject(session_id, "list packs")
prompt_inject(session_id, "enable pack: development")

The unified tool for personal rules AND template pack management!