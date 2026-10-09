module.exports = {
  presets: [
    ['@babel/preset-env', {targets: {node: 'current'}}],
    ['@babel/preset-react', {runtime: 'automatic'}], // Enable React 17+ JSX transform
  ],
};
