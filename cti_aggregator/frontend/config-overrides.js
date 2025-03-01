const { override } = require('customize-cra');

module.exports = function(config, env) {
  // Remove the deprecated onBeforeSetupMiddleware and onAfterSetupMiddleware warnings
  if (process.env.NODE_ENV === 'development') {
    config.devServer = {
      ...config.devServer,
      setupMiddlewares: (middlewares, devServer) => {
        // Your custom middleware code here if needed
        return middlewares;
      }
    };
  }
  
  return override()(config, env);
}; 