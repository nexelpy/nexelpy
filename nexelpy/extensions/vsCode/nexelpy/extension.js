const vscode = require('vscode');

const virtualDocuments = new Map();

function activate(context) {
  const contentProvider = new (class {
    provideTextDocumentContent(uri) {
      return virtualDocuments.get(uri.toString()) || '';
    }
  })();

  context.subscriptions.push(
    vscode.workspace.registerTextDocumentContentProvider('nexelpy-vfs', contentProvider)
  );

  function getEmbeddedBlock(document, position) {
    const text = document.getText();
    const offset = document.offsetAt(position);

    const cssRegex = /(?:add_raw_css|raw_css|css)\s*\(\s*("""|''')([\s\S]*?)\1/g;
    let match;
    while ((match = cssRegex.exec(text)) !== null) {
      const start = match.index + match[0].indexOf(match[1]) + 3;
      const end = match.index + match[0].length - 3;
      if (offset >= start && offset <= end) {
        return {
          type: 'css',
          startOffset: start,
          endOffset: end,
          content: match[2]
        };
      }
    }

    const jsRegex = /(?:js|ts|nexcript)\s*\(\s*("""|''')([\s\S]*?)\1/g;
    while ((match = jsRegex.exec(text)) !== null) {
      const start = match.index + match[0].indexOf(match[1]) + 3;
      const end = match.index + match[0].length - 3;
      if (offset >= start && offset <= end) {
        return {
          type: 'javascript',
          startOffset: start,
          endOffset: end,
          content: match[2]
        };
      }
    }

    return null;
  }

  function createPaddedVirtualDocument(document, block) {
    const startPos = document.positionAt(block.startOffset);
    const linePadding = '\n'.repeat(startPos.line);
    const colPadding = ' '.repeat(startPos.character);
    return linePadding + colPadding + block.content;
  }

  const completionProvider = vscode.languages.registerCompletionItemProvider(
    'python',
    {
      async provideCompletionItems(document, position, token, context) {
        const block = getEmbeddedBlock(document, position);
        if (!block) return undefined;

        const ext = block.type === 'css' ? 'css' : 'js';
        const virtualUri = vscode.Uri.parse(`nexelpy-vfs://virtual/${document.uri.path}.${ext}`);
        const virtualContent = createPaddedVirtualDocument(document, block);

        virtualDocuments.set(virtualUri.toString(), virtualContent);

        const vDoc = await vscode.workspace.openTextDocument(virtualUri);
        await vscode.languages.setTextDocumentLanguage(vDoc, block.type);

        const completions = await vscode.commands.executeCommand(
          'vscode.executeCompletionItemProvider',
          virtualUri,
          position,
          context.triggerCharacter
        );

        if (!completions) return undefined;

        const items = completions.items || completions;
        return items.map(item => {
          const newItem = new vscode.CompletionItem(item.label, item.kind);
          newItem.detail = item.detail;
          newItem.documentation = item.documentation;
          newItem.sortText = item.sortText;
          newItem.filterText = item.filterText;
          newItem.insertText = item.insertText;
          newItem.range = undefined;

          return newItem;
        });
      }
    },
    '.', ':', ' ', '"', "'", '/', '-', '@', '<', '(', '{', ';', '$', '#'
  );

  const hoverProvider = vscode.languages.registerHoverProvider('python', {
    async provideHover(document, position) {
      const block = getEmbeddedBlock(document, position);
      if (!block) return undefined;

      const ext = block.type === 'css' ? 'css' : 'js';
      const virtualUri = vscode.Uri.parse(`nexelpy-vfs://virtual/${document.uri.path}.${ext}`);
      const virtualContent = createPaddedVirtualDocument(document, block);

      virtualDocuments.set(virtualUri.toString(), virtualContent);

      const vDoc = await vscode.workspace.openTextDocument(virtualUri);
      await vscode.languages.setTextDocumentLanguage(vDoc, block.type);

      const hovers = await vscode.commands.executeCommand(
        'vscode.executeHoverProvider',
        virtualUri,
        position
      );

      if (hovers && hovers.length > 0) {
        return hovers[0];
      }
      return undefined;
    }
  });

  const colorProvider = vscode.languages.registerColorProvider('python', {
    async provideDocumentColors(document) {
      const text = document.getText();
      const cssRegex = /(?:add_raw_css|raw_css|css)\s*\(\s*("""|''')([\s\S]*?)\1/g;
      let match;
      const allColors = [];

      while ((match = cssRegex.exec(text)) !== null) {
        const start = match.index + match[0].indexOf(match[1]) + 3;
        const end = match.index + match[0].length - 3;
        const block = {
          type: 'css',
          startOffset: start,
          endOffset: end,
          content: match[2]
        };

        const virtualUri = vscode.Uri.parse(`nexelpy-vfs://virtual/${document.uri.path}.css`);
        const virtualContent = createPaddedVirtualDocument(document, block);

        virtualDocuments.set(virtualUri.toString(), virtualContent);

        const vDoc = await vscode.workspace.openTextDocument(virtualUri);
        await vscode.languages.setTextDocumentLanguage(vDoc, 'css');

        const colors = await vscode.commands.executeCommand(
          'vscode.executeDocumentColorProvider',
          virtualUri
        );

        if (colors) {
          colors.forEach(c => {
            allColors.push(new vscode.ColorInformation(c.range, c.color));
          });
        }
      }

      return allColors;
    },

    provideColorPresentations(color, context) {
      return [
        new vscode.ColorPresentation(`rgba(${Math.round(color.red * 255)}, ${Math.round(color.green * 255)}, ${Math.round(color.blue * 255)}, ${color.alpha})`),
        new vscode.ColorPresentation(`#${((1 << 24) + (Math.round(color.red * 255) << 16) + (Math.round(color.green * 255) << 8) + Math.round(color.blue * 255)).toString(16).slice(1)}`)
      ];
    }
  });

  context.subscriptions.push(completionProvider, hoverProvider, colorProvider);
}

function deactivate() {}

module.exports = {
  activate,
  deactivate
};

