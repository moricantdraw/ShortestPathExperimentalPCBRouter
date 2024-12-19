import { startDevServer } from "server"
import { autoroute } from "./index"

await startDevServer({
  solver: autoroute,
  solverName: "Astar-ts",
  port: 3080,
})