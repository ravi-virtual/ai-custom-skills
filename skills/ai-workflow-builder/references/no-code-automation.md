# No-code / Low-code Mapping (n8n, Make, Zapier)

Use a no-code tool when the flow is mostly app-to-app glue, non-developers must maintain it, or you need triggers and credential management out of the box. Use the Python runner when you need version control, tests, custom logic or tight cost control.

Always export the JSON from the tool's editor instead of hand-writing node definitions; node names, versions and parameters change between releases.

## Concept mapping

| Workflow concept | n8n | Make | Zapier |
|---|---|---|---|
| Trigger | Webhook, Schedule, app trigger nodes | Webhook, Schedule, app trigger modules | Trigger step, Schedule, Webhooks |
| Tool / API step | App node or HTTP Request | App module or HTTP module | App action or Webhooks action |
| LLM step | AI / LLM nodes or HTTP Request to the API | AI modules or HTTP module | AI action or Webhooks action |
| Branch on a condition | IF / Switch | Router with filters | Paths, Filter |
| Loop over a list | Loop Over Items | Iterator (+ Aggregator to collect) | Looping |
| Wait / human approval | Wait node, approval by email/Slack, then resume | Sleep, or data store + second scenario | Delay, or a form/approval then continue |
| Retry / failure path | Node retry settings, Error Trigger workflow | Error handler routes (Resume, Ignore, Break, Rollback, Commit) | Auto-replay, error notifications |
| State between runs | Data tables / external DB | Data stores | Storage by Zapier, Tables |
| Secrets | Credentials store | Connections | Connections |

## Translating a YAML spec

1. One trigger per workflow input source.
2. Each `tool` step becomes one node/module; each `llm_*` step becomes an LLM node with the prompt text copied verbatim and `{{inputs.x}}` replaced by the tool's field mapping.
3. `branches` and `next: {if, then, else}` become IF/Switch/Router/Paths.
4. `parallel: true` over a list becomes a loop/iterator with an aggregator afterwards.
5. `on_failure` becomes node-level retry plus an error route that notifies a human.
6. `human_input` becomes a pause node plus a notification (email/Slack) with an approve link.

## Cautions

- Free-text LLM output feeding the next node needs a parsing/validation node; add one after every structured LLM step.
- Credentials, webhook URLs and customer data live in the tool's cloud: check retention and data-processing terms before sending personal data.
- Task/operation-based pricing grows with loops: estimate runs per month times steps per run before choosing.
- Document the scenario (trigger, owner, failure contact) next to the exported JSON in version control.
