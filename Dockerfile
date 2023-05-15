# pull official python base image
FROM python:3.10

# Create a group and user to run our app
ARG APP_USER=appuser
RUN groupadd -r $APP_USER && useradd --no-log-init -r -g $APP_USER $APP_USER

# set work directory
# create the appropriate directories
ENV APP_HOME=/code
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

# install libpq for postgres authentication
RUN apt-get update && \
    apt-get install --no-install-recommends -y libpq-dev

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.
COPY requirements.txt /code/

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy project and install project dependencies
COPY . $APP_HOME

# Change to a non-root user
RUN chown -R $APP_USER:$APP_USER $APP_HOME
USER $APP_USER:$APP_USER