# 使用官方JupyterLab基础镜像
FROM jupyter/base-notebook:latest


COPY ./jupyter_lab_config.py /opt/conda/etc/jupyter/jupyter_lab_config.py

RUN pip install szdx_ln_jupyter_extra 

#RUN pip install jupyterlab-language-pack-zh-CN

# 切换回默认的jovyan用户
USER jovyan

# 设置工作目录
WORKDIR /home/jovyan/work

# 暴露JupyterLab默认端口
EXPOSE 8888

# 启动JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root","--NotebookApp.token=''"]