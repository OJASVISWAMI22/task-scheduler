Create TYPE task_status AS ENUM ('pending','done','in_progress','failed');
Create TYPE operation_type AS ENUM ('Encrypt','Hash','Transform','Decrypt','Decompress');
Create TABLE requests (
  -- Generate uuid for each request
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  -- Username and userId for the user sending request
  user_id varchar NOT NULL,
  user_name varchar NOT NULL,
  -- Status of task in queue
  status task_status NOT NULL DEFAULT 'pending',
  -- Payload to initiate task
  payload TEXT NOT NULL,
  -- Priority of task
  priority INTEGER DEFAULT 1 CHECK (priority in (1,2,3)),
  -- To-Do :- Retry count and maximum times a task should be retryed 
  -- retry_count INTEGER DEFAULT 0,
  -- max_retries INTEGER DEFAULT 5,

  --operation to perform to secure request
  operation operation_type NOT NULL DEFAULT 'Hash',
  -- Timestamp of the task
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  -- To Do :- Lock so that 2 task can not be run at same time 
  --locked_until TIMESTAMP WITH TIME ZONE,
  -- Id of worker
  --To Do :- worker_id TEXT
);

Create TABLE results(
  -- uuid of each request
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  -- request id sent by user
  request_id UUID NOT NULL REFERENCES requests(id),
  -- output  data of processed request
  output_data TEXT NOT NULL,

  -- Processing time in ms and timestamp
  processed_at TIMESTAMP WITH TIME ZONE,
  processing_ms INTEGER

);

Create INDEX index_task_status_priority on requests(status,priority DESC,created_at ASC);
-- To Do:-Create INDEX index_task_locked_until on tasks (locked_until);