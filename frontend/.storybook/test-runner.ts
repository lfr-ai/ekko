import type { TestRunnerConfig } from "@storybook/test-runner";
import { checkA11y, injectAx } from "ax-playwright";

const config: TestRunnerConfig = {
  async preVisit(page) {
    await injectAx(page);
  },
  async postVisit(page) {
    await checkA11y(page, "#storybook-root", {
      detailedReport: true,
      detailedReportOptions: {
        html: true,
      },
    });
  },
};

export default config;
