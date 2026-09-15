import { useState } from "react";
import { loadPromptCatalog } from "@/infrastructure/graphql/prompt-catalog-client";
import { PromptCatalogPage } from "@/presentation/pages/prompt-catalog-page";

export function App(): React.JSX.Element {
  const [includeContent, setIncludeContent] = useState(false);

  return (
    <PromptCatalogPage
      includeContent={includeContent}
      loadCatalog={loadPromptCatalog}
      onIncludeContentChange={setIncludeContent}
    />
  );
}
