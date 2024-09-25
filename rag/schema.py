import pandera as pa


class InsuranceData(pa.DataFrameModel):
    index: pa.typing.Series[int] = pa.Field(nullable=False)
    text: pa.typing.Series[str] = pa.Field(nullable=False)
    type: pa.typing.Series[str] = pa.Field(nullable=False)
    category: pa.typing.Series[str] = pa.Field(nullable=False)
    package: pa.typing.Series[str] = pa.Field(nullable=False)
    article: pa.typing.Series[str] = pa.Field(nullable=False)
    company: pa.typing.Series[str] = pa.Field(nullable=False)
