import { React } from "@reactpy/client";
import type { DjangoFormProps, HttpRequestProps } from "./types";

export class DjangoForm extends React.Component<DjangoFormProps> {
  componentDidMount() {
    const { onSubmitCallback, formId } = this.props;
    const form = document.getElementById(formId) as HTMLFormElement;

    const onSubmitEvent = (event: Event) => {
      event.preventDefault();
      const formData = new FormData(form);

      // Convert the FormData object to a plain object by iterating through it
      // If duplicate keys are present, convert the value into an array of values
      const entries = formData.entries();
      const formDataArray = Array.from(entries);
      const formDataObject = formDataArray.reduce<Record<string, unknown>>(
        (acc, [key, value]) => {
          if (acc[key]) {
            if (Array.isArray(acc[key])) {
              acc[key].push(value);
            } else {
              acc[key] = [acc[key], value];
            }
          } else {
            acc[key] = value;
          }
          return acc;
        },
        {},
      );

      onSubmitCallback(formDataObject);
    };

    if (form) {
      form.addEventListener("submit", onSubmitEvent);
      // Store cleanup function in instance
      (this as any)._cleanup = () => {
        form.removeEventListener("submit", onSubmitEvent);
      };
    }
  }

  componentWillUnmount() {
    if ((this as any)._cleanup) {
      (this as any)._cleanup();
    }
  }

  render() {
    return null;
  }
}

export class HttpRequest extends React.Component<HttpRequestProps> {
  componentDidMount() {
    const { method, url, body, callback } = this.props;
    fetch(url, {
      method: method,
      body: body,
    })
      .then((response) => {
        response
          .text()
          .then((text) => {
            callback(response.status, text);
          })
          .catch(() => {
            callback(response.status, "");
          });
      })
      .catch(() => {
        callback(520, "");
      });
  }

  render() {
    return null;
  }
}
