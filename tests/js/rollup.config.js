import resolve from "rollup-plugin-node-resolve";
import commonjs from "rollup-plugin-commonjs";
import replace from "rollup-plugin-replace";

const { PRODUCTION } = process.env;

export default {
  input: "src/index.js",
  output: {
    file: "../test_app/static/build.js",
    format: "esm",
  },
  plugins: [
    resolve(),
    commonjs(),
    replace({
      "process.env.NODE_ENV": JSON.stringify(
        PRODUCTION ? "production" : "development"
      ),
    }),
  ],
  onwarn: function (warning) {
    // Skip certain warnings

    // should intercept ... but doesn't in some rollup versions
    if (warning.code === "THIS_IS_UNDEFINED") {
      return;
    }

    // console.warn everything else
    console.warn(warning.message);
  },
};
