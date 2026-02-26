import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    orig_content = content
    
    # 1. Add default=lambda: str(uuid.uuid4()) to String primary keys
    # Example: id = Column(String, primary_key=True) -> id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # Some might already have a default or index. We only want to target those ending abruptly or missing default.
    
    content = re.sub(
        r'id\s*=\s*Column\(String,\s*primary_key=True\)', 
        r'id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))', 
        content
    )
    
    # Also handle id = Column(String, primary_key=True, index=True)
    content = re.sub(
        r'id\s*=\s*Column\(String,\s*primary_key=True,\s*index=True\)', 
        r'id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))', 
        content
    )

    # 2. Enums and other logically required columns missing nullable=False
    # Example: status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    # Be careful not to replace things that already have nullable=
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'Column(Enum(' in line and 'nullable=' not in line:
            # Inject nullable=False before the closing parenthesis of Column
            # This is tricky because the line might have nested parentheses.
            # A simple approach: if line ends with `)`, replace with `, nullable=False)`
            if line.rstrip().endswith(')'):
                lines[i] = line.rstrip()[:-1] + ', nullable=False)'
                
    content = '\n'.join(lines)
    
    if content != orig_content:
        # ensure uuid is imported
        if 'uuid.uuid4' in content and 'import uuid' not in content:
            # find first import
            import_idx = content.find('import ')
            if import_idx != -1:
                content = content[:import_idx] + 'import uuid\n' + content[import_idx:]
            else:
                content = 'import uuid\n' + content
                
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filepath}")

if __name__ == '__main__':
    for root, _, files in os.walk('backend/models'):
        for file in files:
            if file.endswith('.py'):
                fix_file(os.path.join(root, file))
