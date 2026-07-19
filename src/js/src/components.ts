import { React } from "@reactpy/client";
import type { DjangoFormProps, HttpRequestProps } from "./types";

export class DjangoForm extends React.Component<DjangoFormProps> {
  componentDidMount() {
    const { onSubmitCallback, formId } = this.props;
    const form = document.getElementById(formId) as HTMLFormElement;

    const onSubmitEvent = (event: Event) => {
      event.preventDefault();
      const formData = new FormData(form);

      // Accumulate duplicate keys into arrays to support multi-select fields
      // (e.g. MultipleChoiceField). Object.fromEntries would silently drop
      // duplicate entries, keeping only the last value per key.
      const formObject: Record<string, FormDataEntryValue | FormDataEntryValue[]> = {};
      for (const [key, value] of formData.entries()) {
        if (Object.prototype.hasOwnProperty.call(formObject, key)) {
          const existing = formObject[key];
          if (Array.isArray(existing)) {
            existing.push(value);
          } else {
            formObject[key] = [existing, value];
          }
        } else {
          formObject[key] = value;
        }
      }

      onSubmitCallback(formObject);
    };

    if (form) {
      form.addEventListener("submit", onSubmitEvent);
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
