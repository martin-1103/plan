Initialize project dengan database schema dan structure generation dari plan file.

## Usage:
```bash
/init [plan-path] [target-folder]
```

## Parameters:
- `plan-path`: Path ke PRD/plan file (required)
- `target-folder`: Nama target folder untuk project (required)

## What it does:
1. Baca dan analisis PRD/plan file
2. Spawn PARALLEL agents bersamaan:
   - database-schema-designer agent untuk generate optimal database schema
   - project-structure-generator agent untuk generate optimal project structure


## Examples:
```bash
/init @sample_prd.md rbac
/init @docs/plan.txt my-project
/init requirements.md webapp
```

## Notes:
- Generate ANALYSIS dan PLANNING documents only
- Tidak create actual project files
- Output disimpan di `.ai/` folder dengan subfolder sesuai target-folder
- Agents dijalankan secara PARALLEL untuk efisiensi
- **Target-folder parameter diteruskan ke agents:**
  - `database-schema-designer` menerima PRD content + target-folder untuk schema generation
  - `project-structure-generator` menerima PRD content + target-folder untuk digunakan sebagai **root directory name** dalam output tree structure