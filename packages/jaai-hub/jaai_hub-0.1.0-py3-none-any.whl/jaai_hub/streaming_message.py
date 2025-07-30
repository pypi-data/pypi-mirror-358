import inspect
from typing import AsyncGenerator, Generator, List, Literal, Optional, Union

from loguru import logger
from pydantic import BaseModel, Field, field_validator


class Step(BaseModel):
    title: str = Field(
        description="A Short title of the step, specific and short like 'Einloggen bei bahn.de' or 'Bahnverbindungen suchen' in german."
    )
    task: str = Field(
        description="A detailed description of the task that the user wants to accomplish. It will be passed to the agents. You do not want them to ask questions about the task, therefore it should be a detailed description of the task containg all needed information to accomplish the task."
    )
    fulfilled: bool = Field(description="Whether the step has been completed")


class Plan(BaseModel):
    steps: List[Step] = []


class ImageUrl(BaseModel):
    url: str
    score: float


class Source(BaseModel):
    url: Optional[str] = None
    raw_content: Optional[str] = None
    image_urls: Optional[list[ImageUrl]] = None
    title: str


class Attachment(BaseModel):
    type: str
    name: str
    url: Optional[str] = None
    size: Optional[int] = None
    mimeType: Optional[str] = None
    base64: Optional[str] = None
    extractedText: Optional[str] = None


class GeneratedImage(BaseModel):
    url: str
    prompt: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class Status(BaseModel):
    type: Literal["basic", "complete", "error"] = "basic"
    """
    basic: Adds a new status to the list of statuses (uncompleted)
    completed: Marks the message as completed, no more statuses expected
    error: Marks the message as errored
    """
    text: str
    """
    The text of the status to display
    """
    replace: bool = False
    """
    If true, the last status in the list of statuses will be replaced with the new status. Can be used for progress updates.
    """

    @field_validator("type", mode="before")
    def validate_type(cls, v):
        if v not in ["complete", "error"]:
            return "basic"
        return v


class HiddenContext(BaseModel):
    text: str
    """
    The text of the hidden context to display
    """


class StreamedMessage(BaseModel):
    text: str
    sources: list[Source]
    status: list[Status]
    attachments: list[Attachment]
    generated_images: list[GeneratedImage]
    plan: Optional[Plan] = None
    hidden_contexts: list[HiddenContext] = []


StreamableType = Union[str, Source, Status, Attachment, GeneratedImage, Plan, HiddenContext]

SourceGenType = Union[Generator[StreamableType, None, None], AsyncGenerator[StreamableType, None]]


# Events
class Event(BaseModel):
    event: Literal["start", "done", "data", "error", "title_generation"]
    data: Optional[StreamableType] = None
    type: Optional[
        Literal["chunk", "source", "status", "attachment", "generated_image", "plan", "hidden_context"]
    ] = None

    def to_streamable_line(self):
        return f"data: {self.model_dump_json()}\n\n"


def start_event():
    return Event(event="start")


def done_event():
    return Event(event="done")


def title_generation_event(title: str):
    return Event(event="title_generation", data=title)


def error_event(error: str):
    status = Status(type="error", text=error)
    return Event(event="data", data=status, type="status")


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


class StreamingMessage:

    MAX_CHUNK_SIZE = 1000

    def __init__(self, source_gen: SourceGenType):
        self.source_gen = source_gen
        self._is_done = False
        self._text_content = ""
        self._sources = []
        self._status = []
        self._attachments = []
        self._generated_images = []
        self._plan = None
        self._hidden_contexts = []
        self._is_async = inspect.isasyncgen(source_gen)

    def get_message(self):
        return StreamedMessage(
            text=self._text_content,
            sources=self._sources,
            status=self._status,
            attachments=self._attachments,
            generated_images=self._generated_images,
            plan=self._plan,
            hidden_contexts=self._hidden_contexts,
        )

    def is_done(self):
        return self._is_done

    def _process_data(self, data: StreamableType) -> str:
        """Helper method to process each data item from the generator"""
        result = None
        if isinstance(data, Event):
            result = data.to_streamable_line()
        elif isinstance(data, str):
            result = Event(event="data", data=data, type="chunk").to_streamable_line()
            self._text_content += data
        elif isinstance(data, Source):
            result = Event(event="data", data=data, type="source").to_streamable_line()
            self._sources.append(data)
        elif isinstance(data, Status):
            result = Event(event="data", data=data, type="status").to_streamable_line()
            if data.replace and len(self._status) > 0:
                self._status[-1] = data
            else:
                self._status.append(data)
        elif isinstance(data, Attachment):
            result = Event(event="data", data=data, type="attachment").to_streamable_line()
            self._attachments.append(data)
        elif isinstance(data, GeneratedImage):
            result = Event(event="data", data=data, type="generated_image").to_streamable_line()
            self._generated_images.append(data)
        elif isinstance(data, Plan):
            result = Event(event="data", data=data, type="plan").to_streamable_line()
            self._plan = data
        elif isinstance(data, HiddenContext):
            result = Event(event="data", data=data, type="hidden_context").to_streamable_line()
            self._hidden_contexts.append(data)
        elif isinstance(data, list):
            result = Event(event="data", data=str(data), type="chunk").to_streamable_line()
            self._text_content += data
        elif isinstance(data, dict):
            result = Event(event="data", data=str(data), type="chunk").to_streamable_line()
            self._text_content += data
        else:
            logger.warning(f"Unknown data type: {type(data)}. Ignoring.")
        return result

    def __iter__(self):
        if self._is_async:
            raise TypeError("Cannot use __iter__ with an async generator. Use __aiter__ instead.")

        yield Event(event="start").to_streamable_line()
        try:
            for data in self.source_gen:
                result = self._process_data(data)
                if result:
                    yield from chunks(result, self.MAX_CHUNK_SIZE)
        except Exception as e:
            yield from chunks(self._process_data(Status(type="error", text=str(e))), self.MAX_CHUNK_SIZE)
        finally:
            self._is_done = True
            yield Event(event="done").to_streamable_line()

    async def __aiter__(self):
        # If it's a sync generator, we'll convert it to async
        if not self._is_async:
            yield Event(event="start").to_streamable_line()
            try:
                for data in self.source_gen:
                    result = self._process_data(data)
                    if result:
                        for chunk in chunks(result, self.MAX_CHUNK_SIZE):
                            yield chunk
            except Exception as e:
                for chunk in chunks(self._process_data(Status(type="error", text=str(e))), self.MAX_CHUNK_SIZE):
                    yield chunk
            finally:
                self._is_done = True
                yield Event(event="done").to_streamable_line()
            return

        # Handle async generator
        yield Event(event="start").to_streamable_line()
        try:
            async for data in self.source_gen:
                result = self._process_data(data)
                if result:
                    yield result
        except Exception as e:
            for chunk in chunks(self._process_data(Status(type="error", text=str(e))), self.MAX_CHUNK_SIZE):
                yield chunk
        finally:
            yield Event(event="done").to_streamable_line()
            self._is_done = True


class StreamingMessageDecoder:
    def __init__(self):
        self._text_content = ""
        self._sources = []
        self._status = []
        self._attachments = []
        self._generated_images = []
        self._plan = None
        self._hidden_contexts = []
        self._is_done = False
        self._started = False
        self._title = None
        self.buffer = ""

    def process_chunk(self, chunk: Union[str, bytes]) -> list[Event]:
        if isinstance(chunk, bytes):
            chunk = chunk.decode("utf-8")

        self.buffer += chunk

        lines = self.buffer.split("\n")
        self.buffer = lines.pop() or ""
        events = []

        for line in lines:
            if not line or not line.startswith("data: "):
                continue

            data = Event.model_validate_json(line[6:])
            events.append(data)
            if data.event == "data":
                if data.type == "chunk":
                    self._text_content += data.data
                elif data.type == "source":
                    self._sources.append(data.data)
                elif data.type == "status":
                    if data.data.replace and len(self._status) > 0:
                        self._status[-1] = data.data
                    else:
                        self._status.append(data.data)
                elif data.type == "attachment":
                    self._attachments.append(data.data)
                elif data.type == "generated_image":
                    self._generated_images.append(data.data)
                elif data.type == "plan":
                    self._plan = data.data
                elif data.type == "hidden_context":
                    if not isinstance(data.data, HiddenContext):
                        logger.error(f"Invalid hidden_context data type: {type(data.data)}, expected HiddenContext")
                        continue
                    self._hidden_contexts.append(data.data)
            elif data.event == "title_generation":
                self._title = data.data
            elif data.event == "done":
                self._is_done = True
            elif data.event == "error":
                raise Exception(data.data)
            elif data.event == "start":
                self._started = True

        return events

    def consume_chunks(self, chunks: Generator[Union[str, bytes], None, None]):
        for chunk in chunks:
            self.process_chunk(chunk)

    async def consume_chunks_async(self, chunks: AsyncGenerator[Union[str, bytes], None]):
        async for chunk in chunks:
            self.process_chunk(chunk)

    def get_message(self):
        return StreamedMessage(
            text=self._text_content,
            sources=self._sources,
            status=self._status,
            attachments=self._attachments,
            generated_images=self._generated_images,
            plan=self._plan,
            hidden_contexts=self._hidden_contexts,
        )

    def is_done(self):
        return self._is_done

    def get_title(self):
        return self._title


class StreamingMessageForwarder:
    def __init__(self, message_stream: Union[Generator[str, None, None], AsyncGenerator[str, None]]):
        self.message_stream = message_stream
        self.is_async = inspect.isasyncgen(message_stream)
        self.decoder = StreamingMessageDecoder()

    def __iter__(self):
        for chunk in self.message_stream:
            self.decoder.process_chunk(chunk)
            yield chunk

    async def __aiter__(self):
        if self.is_async:
            async for chunk in self.message_stream:
                self.decoder.process_chunk(chunk)
                yield chunk
        else:
            for chunk in self.message_stream:
                self.decoder.process_chunk(chunk)
                yield chunk

    def is_done(self):
        return self.decoder.is_done()

    def get_message(self):
        return self.decoder.get_message()


async def exhaust_streaming_message(streaming_message: Union[StreamingMessage, StreamingMessageForwarder]):
    async for _ in streaming_message:
        pass
