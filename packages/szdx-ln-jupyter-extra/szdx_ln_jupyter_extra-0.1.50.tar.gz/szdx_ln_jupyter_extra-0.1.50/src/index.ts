import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  IRouter
} from '@jupyterlab/application';
import { ICommandPalette } from '@jupyterlab/apputils';
import { IStatusBar } from '@jupyterlab/statusbar';
import createVersion from './widgets/createVersion';
import VersionListSidebarWidget from './widgets/version';
import DataSetListSidebarWidget from './widgets/dataset';
import UsageTimeWidget from './widgets/time';
import TitleWidget from './widgets/title';
import { getProjectDetail, getTaskDetail } from './api/project';
import { Notification } from '@jupyterlab/apputils';
import VariableInspectorPlugins from './widgets/variable/index';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

/**
 * 更新自动保存时间间隔
 * @param settingRegistry - JupyterLab 的设置注册实例
 * @param interval - 自动保存时间间隔（以毫秒为单位，例如 30000 表示 30 秒）
 */
async function updateAutosaveInterval(
  settingRegistry: ISettingRegistry,
  interval: number
) {
  const settingId = '@jupyterlab/docmanager-extension:plugin'; // 设置插件的 ID
  try {
    // 加载当前的设置
    const settings = await settingRegistry.load(settingId);
    // 更新 autosaveInterval 配置
    await settings.set('autosaveInterval', interval);
  } catch (error) {
    console.error('Failed to update autosave interval:', error);
  }
}

/**
 * Activate the ln-notebook extension.
 *
 * @param app - The JupyterLab Application instance
 * @param palette - The command palette instance
 * @param restorer - The application layout restorer
 * @param statusBar - The status bar instance
 *
 * @returns A promise that resolves when the extension has been activated
 */

async function activate(
  app: JupyterFrontEnd,
  palette: ICommandPalette,
  restorer: ILayoutRestorer | null,
  statusBar: IStatusBar,
  router: IRouter | undefined,
  settingRegistry: ISettingRegistry
): Promise<void> {
  console.log('Activating szdx-szdx-ln-jupyter-extra extension...');
  updateAutosaveInterval(settingRegistry, 30);

  await new Promise(resolve => setTimeout(resolve, 100));
  if (router) {
    // 尝试获取路由信息的备选方案
    const currentUrl = window.location.href;
    const pathSegments = currentUrl.split('/');
    const taskId = pathSegments[4];
    const taskData = await getTaskDetail(taskId);
    const notebookProjectId = taskData.notebookProjectId;
    const inputVolumeItem = taskData.jobStorageList.find(
      (item: any) => item.businessType === 0
    );
    const inputVolume = inputVolumeItem?.volumeTo || '';

    if (inputVolume) {
      app.serviceManager.contents
        .get(inputVolume)
        .then(result => {
          if (result.content[0].path) {
            app.commands.execute('filebrowser:open-path', {
              path: result.content[0].path
            });
          }
          console.log(result.content[0].path);
        })
        .catch(error => {
          console.error('路径不存在或无法访问:', error);
        });
    }

    if (!notebookProjectId) {
      Notification.error('项目ID未获取到', { autoClose: 3000 });
    } else {
      try {
        console.log('Initial route:', notebookProjectId || 'Route not ready');

        const projectData = await getProjectDetail(notebookProjectId || '');
        const teachingId = projectData.originId;
        const roleType = projectData.roleType;
        const originVersionId = projectData.projectVersionList[0]?.id || '';
        const timeWidget = new UsageTimeWidget(taskId);
        timeWidget.install(app);

        const sidebarVersion = new VersionListSidebarWidget(
          app,
          notebookProjectId
        );
        sidebarVersion.install(app);

        const sidebarDataSet = new DataSetListSidebarWidget({ projectData });
        sidebarDataSet.install(app);

        const titleWidget = new TitleWidget({ projectData });
        titleWidget.install(app);

        const createVersionBtn = new createVersion(
          app,
          notebookProjectId,
          teachingId,
          roleType,
          originVersionId
        );
        createVersionBtn.install(app);

        console.log('szdx-szdx-ln-jupyter-extra extension activated successfully!');
      } catch (error) {
        console.error('Error during activation:', error);
        Notification.error('插件激活失败');
      }
    }
  }
}

const lnPlugin: JupyterFrontEndPlugin<void> = {
  id: 'ln-notebook:plugin',
  description: 'leinao extra jupyter plugin',
  autoStart: true,
  requires: [
    ICommandPalette,
    ILayoutRestorer,
    IStatusBar,
    IRouter,
    ISettingRegistry
  ],
  activate: activate
};

const plugins = [lnPlugin, ...VariableInspectorPlugins];
export default plugins;
