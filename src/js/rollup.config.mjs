import resolve from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";
import replace from "@rollup/plugin-replace";
import typescript from "@rollup/plugin-typescript";

export default {
  input: "src/index.tsx",
  output: {
    file: "../reactpy_django/static/reactpy_django/client.js",
    format: "esm",
  },
  plugins: [
    resolve(),
    commonjs(),
    replace({
      "process.env.NODE_ENV": JSON.stringify("production"),
    }),
    typescript(),
  ],
  onwarn: function (warning) {
    console.warn(warning.message);
  },
};
