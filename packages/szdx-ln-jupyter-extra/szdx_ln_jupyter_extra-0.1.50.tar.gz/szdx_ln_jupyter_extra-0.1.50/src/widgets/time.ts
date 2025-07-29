import { Widget } from '@lumino/widgets';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { getTaskDetail } from '../api/project';
import { Notification } from '@jupyterlab/apputils';

function computedDurTime(time: number) {
  if (time) {
    if (time <= 1) {
      return '1s';
    }
    const elapsedTime = Math.round(time / 1000);
    let result = '';
    const elapsedDay = parseInt((elapsedTime / (24 * 60 * 60)) as any);
    if (elapsedDay > 0) {
      result += elapsedDay + 'd ';
    }
    const elapsedHour = parseInt(
      ((elapsedTime % (24 * 60 * 60)) / (60 * 60)) as any
    );
    if (result !== '' || (result === '' && elapsedHour > 0)) {
      result += elapsedHour + 'h ';
    }
    const elapsedMinute = parseInt(((elapsedTime % (60 * 60)) / 60) as any);
    if (result !== '' || (result === '' && elapsedMinute > 0)) {
      result += elapsedMinute + 'm ';
    }
    const elapsedSecond = parseInt((elapsedTime % 60) as any);
    result += elapsedSecond + 's';
    return result;
  } else {
    return '--';
  }
}

class UsageTimeWidget extends Widget {
  startTime: number; // 添加类型声明
  taskId: string;
  constructor(taskId: string) {
    super();
    this.taskId = taskId;
    this.id = 'usage-time-widget';
    this.title.label = '使用时间';
    this.title.closable = true;
    this.addClass('usage-time-widget');
    this.startTime = 0; // 记录启动时间
    this.updateUsageTime();

    setInterval(() => this.updateUsageTime(), 60000); // 每秒更新
  }

  async updateUsageTime() {
    const taskId = this.taskId || '';
    if (taskId) {
      const taskData = await getTaskDetail(taskId);
      const { completedTime, startedTime, state } = taskData;
      const usedTime = completedTime
        ? computedDurTime(completedTime - startedTime)
        : state === 'Running'
          ? computedDurTime(new Date().getTime() - startedTime)
          : undefined;
      this.node.innerText = `已使用时间: ${usedTime} `;
    } else {
      Notification.error('任务ID未获取到', { autoClose: 3000 });
    }
  }

  install(app: JupyterFrontEnd) {
    app.shell.add(this, 'top', {
      rank: 998
    });
  }
}

export default UsageTimeWidget;
