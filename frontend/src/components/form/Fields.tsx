import { ChevronDownIcon } from "@heroicons/react/16/solid";

const LABEL = "block text-sm/6 font-medium text-gray-900 dark:text-white";
const INPUT =
  "block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-indigo-500";
const SELECT =
  "col-start-1 row-start-1 w-full appearance-none rounded-md bg-white py-1.5 pr-8 pl-3 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-indigo-600 sm:text-sm/6 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:*:bg-gray-800 dark:focus-visible:outline-indigo-500";

type TextFieldProps = {
  id: string;
  label: string;
  /** Omit for display-only inputs that should not be submitted. */
  name?: string;
  type?: "text" | "email" | "number";
  placeholder?: string;
  required?: boolean;
  min?: number;
  value?: string;
  readOnly?: boolean;
};

export function TextField({ id, label, type = "text", ...input }: TextFieldProps) {
  return (
    <div>
      <label htmlFor={id} className={LABEL}>
        {label}
      </label>
      <div className="mt-2">
        <input id={id} type={type} className={INPUT} {...input} />
      </div>
    </div>
  );
}

type SelectFieldProps = {
  id: string;
  label: string;
  options: ReadonlyArray<string | { value: string; label: string }>;
};

export function SelectField({ id, label, options }: SelectFieldProps) {
  return (
    <div>
      <label htmlFor={id} className={LABEL}>
        {label}
      </label>
      <div className="mt-2 grid grid-cols-1">
        <select id={id} name={id} defaultValue="" className={SELECT}>
          <option value="">—</option>
          {options.map((o) => {
            const { value, label } = typeof o === "string" ? { value: o, label: o } : o;
            return (
              <option key={value} value={value}>
                {label}
              </option>
            );
          })}
        </select>
        <ChevronDownIcon
          aria-hidden="true"
          className="pointer-events-none col-start-1 row-start-1 mr-2 size-5 self-center justify-self-end text-gray-500 sm:size-4 dark:text-gray-400"
        />
      </div>
    </div>
  );
}
