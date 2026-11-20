// Nguon goc: dung tren ma nguon LinguaGacha (https://github.com/neavo/LinguaGacha, tac gia neavo).
// Dung theo dieu kien cua tac gia: ghi nguon, khong thuong mai.
// vgt bridge: chạy backend LinguaGacha 0.132.1 không cần Electron, KHÔNG gọi model.
// extract: tạo dự án .lg từ thư mục game (chỉ đọc chữ); generate: xuất bản dịch từ .lg ra thư mục riêng.
import path from "node:path";
import { BackendResources } from "./backend/bootstrap/backend-resources";
import { BackendServices } from "./backend/bootstrap/backend-services";

function arg(name: string): string {
  const i = process.argv.indexOf("--" + name);
  if (i < 0 || i + 1 >= process.argv.length) throw new Error("missing --" + name);
  return path.resolve(process.argv[i + 1]!);
}
function opt(name: string, dflt: string): string {
  const i = process.argv.indexOf("--" + name);
  return i < 0 ? dflt : process.argv[i + 1]!;
}

async function main(): Promise<void> {
  const cmd = process.argv[2];
  const resources = await BackendResources.start({
    appRoot: arg("app-root"),
    builtinRoot: arg("builtin"),
    logTargets: { console: false, window: false },
    proxyResolver: { resolveProxy: async () => "DIRECT" },
  });
  const services = new BackendServices({
    paths: resources.paths,
    metadata: resources.metadata,
    appSettingService: resources.settings,
    database: resources.database,
    logManager: resources.logManager,
    publishEvent: () => undefined,
    openOutputFolder: async () => undefined,
    workerExecution: { kind: "in_process" },
  });
  try {
    if (cmd === "extract") {
      const created = await services.project.lifecycle.create_project_commit(
        {
          path: arg("project"),
          source_paths: [arg("game")],
          languages: { source_language: opt("src-lang", "JA"), target_language: opt("tgt-lang", "VI") },
        },
        () => undefined,
      );
      const { entries } = (await services.project.summary.read()).snapshot;
      process.stdout.write(JSON.stringify({ ok: true, source_operation: (created as any)?.source_operation, entries: entries.length }) + "\n");
      await services.project.lifecycle.unload_project();
    } else if (cmd === "generate") {
      await services.project.lifecycle.load_project({ path: arg("project") });
      const r = await services.files.translationGeneration.generate_files_to_directory(arg("out"), []);
      process.stdout.write(JSON.stringify({ ok: true, result: r }) + "\n");
      await services.project.lifecycle.unload_project();
    } else throw new Error("usage: extract|generate");
  } finally {
    await services.dispose();
    await resources.dispose();
  }
}
main().catch((e) => { process.stderr.write((e && e.stack) || String(e)); process.stderr.write("\n"); process.exit(1); });
