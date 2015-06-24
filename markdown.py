from flaskext.markdown import Extension, Markdown
from preprocessors import SimplePreprocessor
markdown_instance = Markdown(app)

@markdown_instance.make_extension()
class SimpleExtension(Extension):
     def extendMarkdown(self, md, md_globals):
         md.preprocessors.add('prover_block',
                          SimplePreprocessor(md),
                          '_begin')
     md.registerExtension(self)
