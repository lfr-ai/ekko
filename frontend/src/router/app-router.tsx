import { createBrowserRouter } from "react-router";
import { HomePage } from "@/presentation/pages/home-page";

export const appRouter = createBrowserRouter([
  {
    element: <HomePage />,
    path: "/",
  },
]);
