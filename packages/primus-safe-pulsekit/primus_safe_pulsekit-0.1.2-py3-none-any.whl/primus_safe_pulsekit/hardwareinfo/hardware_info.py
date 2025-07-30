from pydantic import BaseModel, Field
from .cpu import CPUInfo
from .gpu import GPUInfo
from .ethernet import EthernetInfo
from .memory import MemoryInfo

class HardwareInfo(BaseModel):
    cpu: CPUInfo = Field(default_factory=CPUInfo)
    gpu: GPUInfo = Field(default_factory=GPUInfo)
    memory: MemoryInfo = Field(default_factory=MemoryInfo)
    ethernet: EthernetInfo = Field(default_factory=EthernetInfo)

    def load(self):
        for name, component in self.__dict__.items():
            if component is not None and hasattr(component, 'load') and callable(getattr(component, 'load')):
                try:
                    component.load()
                except Exception as e:
                    print(f"Failed to load {name}: {e}")

    def print_summary(self):
        for name, component in self.__dict__.items():
            if component is not None and hasattr(component, 'print_summary') and callable(getattr(component, 'print_summary')):
                try:
                    print(f"{name}:")
                    component.print_summary()
                except Exception as e:
                    print(f"Failed to print_summary {name}: {e}")
