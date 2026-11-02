import { readFile } from "node:fs/promises";
import { glob } from "node:fs/promises";
import { parse } from "graphql";

const DOCUMENT_GLOB = "src/infrastructure/graphql/operations/**/*.graphql";

async function validateDocuments() {
  const invalidDocuments = [];

  for await (const filePath of glob(DOCUMENT_GLOB)) {
    const rawContent = await readFile(filePath, "utf-8");

    try {
      parse(rawContent);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown parse error.";
      invalidDocuments.push({ filePath, message });
    }
  }

  if (invalidDocuments.length === 0) {
    console.log("GraphQL document validation passed.");
    return;
  }

  console.error("GraphQL document validation failed:");
  for (const documentIssue of invalidDocuments) {
    console.error(`- ${documentIssue.filePath}: ${documentIssue.message}`);
  }

  process.exitCode = 1;
}

await validateDocuments();
