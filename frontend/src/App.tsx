import { useState } from "react";
import { summarizeChunks } from "@/infrastructure/api/summarize-client";
import { loadPromptCatalog } from "@/infrastructure/graphql/prompt-catalog-client";
import { PromptCatalogPage } from "@/presentation/pages/prompt-catalog-page";
import { SummarizePage } from "@/presentation/pages/summarize-page";

export function App(): React.JSX.Element {
  const [includeContent, setIncludeContent] = useState(false);

  return (
    <>
      <SummarizePage summarize={summarizeChunks} />
      <PromptCatalogPage
        includeContent={includeContent}
        loadCatalog={loadPromptCatalog}
        onIncludeContentChange={setIncludeContent}
      />
    </>
  );
}
