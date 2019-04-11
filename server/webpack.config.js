const path = require('path')

const config = {
    context: __dirname,
    entry: './src/index.jsx',
    devtool: 'cheap-eval-source-map',
    output: {
        path: path.join(__dirname, 'public'),
        filename: 'index.js'
    },
    resolve: {
        extensions: ['.jsx', 'js']
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                loader: 'babel-loader',
                query: {
                  presets: ['@babel/react'],
                  plugins: ['@babel/proposal-class-properties']
                },
            }
        ]
    },
    resolve: {
    extensions: ['.js', '.jsx'],
  },
  mode: "development"
}

module.exports = config