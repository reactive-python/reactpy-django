export interface DjangoFormProps {
  onSubmitCallback: (data: object) => void;
  formId: string;
}

export interface HttpRequestProps {
  method: string;
  url: string;
  body: string;
  callback: (status: number, response: string) => void;
}
