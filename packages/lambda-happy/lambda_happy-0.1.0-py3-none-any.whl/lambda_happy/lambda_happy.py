import torch
import lib_lambda


class LambdaHappy:
    """
    Compute the “lambda happy” statistic with very explicit, verbose method names.

    Constructor arguments:
      - X       : input torch.Tensor (infers device & dtype), or None to generate random
      - m       : number of random projections (default: 10_000)
      - version : one of {"DEFAULT", "CUSTOM", "PYTORCH"}
          DEFAULT → automatic dispatch by device & dtype
          CUSTOM  → force C++ when available (GPU + float32), else PyTorch
          PYTORCH → always PyTorch implementations
    """
    VALID_VERSIONS = {"DEFAULT", "CUSTOM", "PYTORCH"}

    def __init__(self,
                 X: torch.Tensor = None,
                 m: int = 10_000,
                 version: str = "DEFAULT"):
        if version not in self.VALID_VERSIONS:
            raise ValueError(f"version must be one of {self.VALID_VERSIONS}")
        self.m = m
        self.version = version

        if X is None:
            # Default to CPU float32 random data
            self._X = torch.randn(1_000, 10_000, dtype=torch.float32, device="cpu")
        else:
            self._X = X

        # Infer once
        self._device_type = self._X.device.type   # 'cpu' or 'cuda'
        self._dtype = self._X.dtype               # torch.float32 or torch.float16

        # Dispatch tables
        self._default_dispatch = {
            ("cuda", torch.float32): self._compute_gpu_f32_cpp,
            ("cuda", torch.float16): self._compute_gpu_f16_pytorch,
            ("cpu",  torch.float32): self._compute_cpu_f32_pytorch,
            ("cpu",  torch.float16): self._compute_cpu_f16_pytorch,
        }
        self._cpp_dispatch = {
            ("cuda", torch.float32): self._compute_gpu_f32_cpp,
            ("cuda", torch.float16): self._compute_gpu_f16_pytorch,
            ("cpu",  torch.float32): self._compute_cpu_f32_pytorch,
            ("cpu",  torch.float16): self._compute_cpu_f16_pytorch,
        }
        self._pytorch_dispatch = {
            ("cuda", torch.float32): self._compute_gpu_f32_pytorch,
            ("cuda", torch.float16): self._compute_gpu_f16_pytorch,
            ("cpu",  torch.float32): self._compute_cpu_f32_pytorch,
            ("cpu",  torch.float16): self._compute_cpu_f16_pytorch,
        }

    def compute_lambda_happy(self) -> float:
        """
        Top-level dispatch according to `version`:
          1) DEFAULT → default_dispatch
          2) CUSTOM  → cpp_dispatch
          3) PYTORCH → pytorch_dispatch
        """
        key = (self._device_type, self._dtype)

        if self.version == "DEFAULT":
            impl = self._default_dispatch.get(key)
        elif self.version == "CUSTOM":
            impl = self._cpp_dispatch.get(key)
        elif self.version == "PYTORCH":
            impl = self._pytorch_dispatch.get(key)
        else:
            impl = None

        if impl is None:
            raise RuntimeError(f"No implementation for device={self._device_type}, dtype={self._dtype}")

        return impl()

    # ---- C++ (CUSTOM) implementations ----

    def _compute_gpu_f32_cpp(self) -> float:
        """
        GPU + float32 via native C++ (lib_lambda).
        """
        Xc = self._X.contiguous().to(device="cuda", dtype=torch.float32)
        return lib_lambda.compute_lambda_happy(Xc, self.m)

    def _compute_gpu_f16_cpp(self) -> float:
        """
        GPU + float16 via C++ (not supported) → fallback to PyTorch fp16.
        """
        return self._compute_gpu_f16_pytorch()

    # ---- PyTorch implementations ----

    def _compute_gpu_f32_pytorch(self) -> float:
        """
        GPU + float32 via PyTorch.
        """
        return self._pytorch_compute(device="cuda", dtype=torch.float32)

    def _compute_gpu_f16_pytorch(self) -> float:
        """
        GPU + float16 via PyTorch.
        """
        return self._pytorch_compute(device="cuda", dtype=torch.float16)

    def _compute_cpu_f32_pytorch(self) -> float:
        """
        CPU + float32 via PyTorch.
        """
        return self._pytorch_compute(device="cpu", dtype=torch.float32)

    def _compute_cpu_f16_pytorch(self) -> float:
        """
        CPU + float16 via PyTorch.
        """
        return self._pytorch_compute(device="cpu", dtype=torch.float16)

    # ---- Shared helper for all PyTorch paths ----

    def _pytorch_compute(self, device: str, dtype: torch.dtype) -> float:
        """
        Shared PyTorch routine:
          - moves X to (device, dtype)
          - generates Z of same shape & type
          - computes Chebyshev norm of XᵀZ and l2-norm of Z rows
          - returns the 0.95-quantile of λ = numer/denom as float
        """
        X = self._X.to(device=device, dtype=dtype)
        n = X.shape[0]
        Z = torch.randn(n, self.m, device=device, dtype=dtype)
        Z.sub_(Z.mean(dim=0, keepdim=True))
        numer = torch.linalg.norm(X.T @ Z, ord=float("inf"), dim=0)
        denom = torch.linalg.norm(Z, ord=2, dim=0)
        lambdas = (numer / denom).to(torch.float32)
        return torch.quantile(lambdas, 0.95).item()
