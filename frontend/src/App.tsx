import { RouterProvider } from "react-router";
import { appRouter } from "@/router/app-router";

export function App(): React.JSX.Element {
  return <RouterProvider router={appRouter} />;
}
