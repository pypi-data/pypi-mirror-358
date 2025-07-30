# Desktop Commander Tool Instructions

You have access to desktop-commander with comprehensive file system and development capabilities.

## Key Capabilities
- **File Operations**: read_file, write_file, list_directory, move_file, search_files
- **Code Operations**: search_code, edit_block  
- **Command Execution**: execute_command, read_output
- **Process Management**: list_processes, kill_process

## Best Practices

### File Operations
- **Always use absolute paths** for reliability (start with `/` or drive letter)
- **Use read_file instead of cat/type commands** - it's optimized and handles large files better
- **Chunk large file writes** - write files in ≤30 line chunks using write_file with append mode
- **Use search_files for finding files by name**, search_code for finding code patterns

### Code Changes  
- **Surgical edits**: Use edit_block for precise changes instead of rewriting entire files
- **Include minimal context** in edit_block operations - just enough to uniquely identify the location
- **Read first, then edit**: Always read_file to understand current state before making changes

### Command Execution
- **Prefer specialized tools** over generic commands (use read_file vs cat, list_directory vs ls)
- **Use absolute paths in commands** to avoid current directory issues
- **For long-running processes**: Let the human run them - your read_output throughput is limited

## Common Patterns

### File Analysis Workflow
1. `list_directory` - Explore project structure
2. `read_file` - Examine key files  
3. `search_code` - Find relevant patterns
4. Analyze and provide insights

### Code Modification Workflow  
1. `search_code` - Find target code locations
2. `read_file` - Understand current implementation
3. `edit_block` - Make precise surgical changes
4. Verify changes if needed

### Project Exploration
1. `list_directory` - Start with project root
2. `read_file` key files (README, package.json, etc.)
3. `search_files` - Find files matching patterns
4. `search_code` - Understand code organization

## Performance Tips
- Batch related file operations together
- Use search tools to avoid reading unnecessary files  
- Prefer edit_block over full file rewrites
- Use chunked writes for large content
