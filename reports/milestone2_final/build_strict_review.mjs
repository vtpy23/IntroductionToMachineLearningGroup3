/** Reuse the established editable PptxGenJS design; no experiment execution. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=path.dirname(fileURLToPath(import.meta.url));
const BUILD=path.join(HERE,'.build/strict-review');
await fs.mkdir(BUILD,{recursive:true});
let wrapper=await fs.readFile(path.join(HERE,'build_three_seeds.mjs'),'utf8');
wrapper=wrapper.replace('const HERE=path.dirname(fileURLToPath(import.meta.url));',`const HERE=${JSON.stringify(HERE)};`)
 .replaceAll('.build/three-seeds','.build/strict-review')
 .replaceAll('slide_content_three_seeds.json','slide_content_strict.json');
const patches=await fs.readFile(path.join(HERE,'../strict_review/layout_overrides.mjs'),'utf8');
const marker="await fs.writeFile(path.join(BUILD,'generated-builder.mjs'),code,'utf8');";
if(!wrapper.includes(marker))throw new Error('Design builder entry point changed');
wrapper=wrapper.replace(marker,patches+'\n'+marker);
await fs.writeFile(path.join(BUILD,'strict-wrapper.mjs'),wrapper,'utf8');
await import(pathToFileURL(path.join(BUILD,'strict-wrapper.mjs')).href+'?t='+Date.now());
