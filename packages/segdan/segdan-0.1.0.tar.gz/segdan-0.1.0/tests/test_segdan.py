from segdan.converters import ConverterFactory, Converter

factory = ConverterFactory()
args = {"input_data": r"", "output_dir":r"","img_dir":r"", "background":3}
converter_1 = factory.get_converter("txt", "mask", args)

print(converter_1.__class__)