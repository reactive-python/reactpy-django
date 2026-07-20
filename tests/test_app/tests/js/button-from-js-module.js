import { h, render } from "https://unpkg.com/preact?module";

export function bind(node, config) {
  return {
    create: (type, props, children) => h(type, props, ...children),
    render: (element) => render(element, node),
    unmount: () => render(null, node),
  };
}

export function SimpleButton(props) {
  return h(
    "button",
    {
      id: props.id,
    },
    "simple button",
  );
}
