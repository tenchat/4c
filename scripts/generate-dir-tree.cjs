const fs = require('fs')
const path = require('path')

const IGNORE_DIRS = new Set([
  'node_modules',
  '.git',
  '.husky',
  '.vscode',
  '.history',
  'dist',
  '.pytest_cache',
  '__pycache__',
  '.pyenv',
  'venv',
  '.venv'
])

const IGNORE_FILES = new Set([
  '.DS_Store',
  'Thumbs.db',
  '.gitignore',
  '.gitattributes',
  '.env',
  '.env.development',
  '.env.production',
  '.prettierignore',
  '.stylelintignore',
  'package-lock.json',
  'pnpm-lock.yaml',
  'yarn.lock'
])

function generateTree(dir, prefix = '', isLast = true) {
  const items = fs.readdirSync(dir, { withFileTypes: true })
  const dirs = []
  const files = []

  items.forEach((item) => {
    if (item.isDirectory()) {
      if (!IGNORE_DIRS.has(item.name)) {
        dirs.push(item.name)
      }
    } else {
      if (!IGNORE_FILES.has(item.name)) {
        files.push(item.name)
      }
    }
  })

  // Sort alphabetically, dirs before files
  dirs.sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }))
  files.sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }))

  const allItems = [
    ...dirs.map((n) => ({ name: n, isDir: true })),
    ...files.map((n) => ({ name: n, isDir: false }))
  ]

  let result = ''
  const linePrefix = isLast ? '└── ' : '├── '

  allItems.forEach((item, index) => {
    const isLastItem = index === allItems.length - 1
    const currentPrefix = prefix + (isLastItem ? '    ' : '│   ')
    const connector = isLastItem ? '└── ' : '├── '

    result += `${prefix}${connector}${item.name}${item.isDir ? '/' : ''}\n`

    if (item.isDir) {
      const subPath = path.join(dir, item.name)
      result += generateTree(subPath, currentPrefix, true)
    }
  })

  return result
}

function getProjectName() {
  const pkgPath = path.join(process.cwd(), 'package.json')
  if (fs.existsSync(pkgPath)) {
    const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'))
    return pkg.name || 'project'
  }
  return path.basename(process.cwd())
}

function main() {
  const rootDir = process.cwd()
  const projectName = getProjectName()

  let output = `# ${projectName}\n\n`
  output += `> Generated on ${new Date().toISOString().split('T')[0]}\n\n`
  output += '## Directory Structure\n\n'
  output += '```\n'
  output += `${projectName}/\n`
  output += generateTree(rootDir)
  output += '```\n'

  // Collect summary stats
  let totalFiles = 0
  let totalDirs = 0

  function countItems(dir) {
    const items = fs.readdirSync(dir, { withFileTypes: true })
    items.forEach((item) => {
      if (IGNORE_DIRS.has(item.name) || IGNORE_FILES.has(item.name)) return
      if (item.isDirectory()) {
        totalDirs++
        countItems(path.join(dir, item.name))
      } else {
        totalFiles++
      }
    })
  }

  try {
    countItems(rootDir)
    output += `## Summary\n\n`
    output += `- **Total directories**: ${totalDirs}\n`
    output += `- **Total files**: ${totalFiles}\n`
  } catch (e) {
    // Ignore count errors
  }

  const outputPath = path.join(rootDir, 'DIRECTORY_STRUCTURE.md')
  fs.writeFileSync(outputPath, output, 'utf-8')
  console.log(`Directory structure saved to: ${outputPath}`)
}

main()
