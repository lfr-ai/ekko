const { getJestConfig } = require("@storybook/test-runner");

const testRunnerConfig = getJestConfig();

/** @type {import("@jest/types").Config.InitialOptions} */
module.exports = {
  ...testRunnerConfig,
  modulePathIgnorePatterns: [
    ...(testRunnerConfig.modulePathIgnorePatterns ?? []),
    "<rootDir>/frontend/~/",
    "<rootDir>/frontend/dist/",
    "<rootDir>/frontend/storybook-static/",
  ],
};
