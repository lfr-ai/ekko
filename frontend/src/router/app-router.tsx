import { createBrowserRouter, Navigate } from "react-router";
import { ClaimIntakePage } from "@/presentation/pages/claim-intake-page";

export const appRouter = createBrowserRouter([
  {
    element: <Navigate replace to="/claims/intake" />,
    path: "/",
  },
  {
    element: <ClaimIntakePage />,
    path: "/claims/intake",
  },
]);
