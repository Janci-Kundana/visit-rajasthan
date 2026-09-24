import fs from "node:fs/promises";
import path from "node:path";
import { promisify } from "node:util";
import zlib from "node:zlib";
import { defineConfig, type Plugin } from "vite";

const gzip = promisify(zlib.gzip);
const brotli = promisify(zlib.brotliCompress);

const COMPRESSIBLE = new Set([".glb", ".webp", ".png", ".js", ".css", ".html"]);

async function listFiles(dir: string): Promise<string[]> {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const nested = await Promise.all(
    entries.map((entry) => {
      const full = path.join(dir, entry.name);
      return entry.isDirectory() ? listFiles(full) : [full];
    }),
  );
  return nested.flat();
}

/**
 * Writes `.gz` and `.br` siblings for every shipped asset so the host can serve
 * precompressed bytes. Runs in `closeBundle`, after Vite has copied `public/`
 * into the output directory, so the Blender models and posters are included.
 */
function precompress(): Plugin {
  let outDir = "dist";
  return {
    name: "visit-rajasthan:precompress",
    apply: "build",
    configResolved(config) {
      outDir = path.resolve(config.root, config.build.outDir);
    },
    async closeBundle() {
      const files = (await listFiles(outDir)).filter((file) =>
        COMPRESSIBLE.has(path.extname(file).toLowerCase()),
      );
      await Promise.all(
        files.map(async (file) => {
          const source = await fs.readFile(file);
          const [gz, br] = await Promise.all([
            gzip(source, { level: 9 }),
            brotli(source, {
              params: {
                [zlib.constants.BROTLI_PARAM_QUALITY]: 9,
                [zlib.constants.BROTLI_PARAM_SIZE_HINT]: source.length,
              },
            }),
          ]);
          await Promise.all([fs.writeFile(`${file}.gz`, gz), fs.writeFile(`${file}.br`, br)]);
        }),
      );
    },
  };
}

export default defineConfig({
  base: "./",
  server: {
    port: 5173,
  },
  plugins: [precompress()],
});
