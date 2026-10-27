/* Auditable parity probe: read synthetic file only; never writes or fetches.
 * Raw genotype values not printed. Uses same browser Blob.stream() semantics.
 */
import {readFileSync} from "node:fs";
import {parseArray} from "./analysis-core.mjs";
const file=readFileSync(process.argv[2]);
const data=await parseArray({size:file.byteLength,stream:()=>new Blob([file]).stream()});
console.log(JSON.stringify({build:data.qc.build,valid:data.qc.valid,
 no_calls:data.qc.no_calls,duplicates:data.qc.duplicates,
 conflicts:data.qc.conflicts,rejected:data.qc.rejected,
 typed_status:Object.fromEntries(["rs601338","rs855791"].map(r=>[r,data.calls.has(r)]))
}));
