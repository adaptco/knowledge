const fs = require('fs');
const path = require('path');

describe('VS Code Configuration', () => {
  let launchConfig;
  let tasksConfig;

  beforeAll(() => {
    const launchJsonPath = path.resolve(__dirname, 'launch.json');
    const tasksJsonPath = path.resolve(__dirname, 'tasks.json');

    const launchJsonContent = fs.readFileSync(launchJsonPath, 'utf8');
    const tasksJsonContent = fs.readFileSync(tasksJsonPath, 'utf8');

    // Remove trailing commas from JSON files to avoid parsing errors
    const cleanedLaunchJson = launchJsonContent.replace(/,(?=\s*?[\}\]])/g, '');
    const cleanedTasksJson = tasksJsonContent.replace(/,(?=\s*?[\}\]])/g, '');

    launchConfig = JSON.parse(cleanedLaunchJson);
    tasksConfig = JSON.parse(cleanedTasksJson);
  });

  test('launch.json should be a valid JSON', () => {
    expect(launchConfig).toBeInstanceOf(Object);
  });

  test('tasks.json should be a valid JSON', () => {
    expect(tasksConfig).toBeInstanceOf(Object);
  });

  test('all preLaunchTasks in launch.json should exist in tasks.json', () => {
    const taskLabels = tasksConfig.tasks.map(task => task.label);

    launchConfig.configurations.forEach(config => {
      if (config.preLaunchTask) {
        expect(taskLabels).toContain(config.preLaunchTask);
      }
    });
  });
});
