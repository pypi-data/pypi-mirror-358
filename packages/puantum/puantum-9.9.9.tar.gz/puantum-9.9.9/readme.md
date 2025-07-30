# 🔐 Python Cryptography

A blazing-fast cryptography library for Python, built on Rust.

Pryptography supports an extensive set of **post-quantum** digital signature algorithms (DSA) and key encapsulation mechanisms (KEM).

---
## ⚡ Features
- ✅ Dozens of NIST PQC candidates 
- 🦀 Rust core for speed and safety
- 📦 Easy installation via [`pip`](https://pip.pypa.io)
---

### 🧬 Supported Algorithms

### 🛡️ KEM
- #### Bike
- #### ClassicMcEliece
- #### Hqc
- #### Kyber
- #### MLKEM
- #### NtruPrime
- #### FrodoKem

### ✍️ DSA
- #### Cross
- #### Dilithium
- #### Falcon
- #### Mayo
- #### MLDSA
- #### Sphincs
- #### Uov

### ❔ Examples

#### DSA Example
```python
# IMPORT
from puantum.quantum.dsa import Algorithm, KeyPair

# MAIN
alicesk, alicepk = KeyPair(Algorithm.MLDSA.MLDSA87)
message = "Hello".encode()

signature = alicesk.sign(message=message)
valid = alicepk.verify(signature=signature, message=message)

assert valid, "Signature verification failed!"

print(f"Message:   [{message.decode()}]")
print(f"Signature: [{signature.hex()[:len(message)]}]")
```

#### KEM Example
```python
# IMPORT
from puantum.quantum.kem import Algorithm, KeyPair

# MAIN
alicesk, alicepk = KeyPair(Algorithm.MLKEM.MLKEM1024)
_bobsk, _bobpk = KeyPair(Algorithm.MLKEM.MLKEM1024)

bobss, bobct = alicepk.encapsulate()
alicess = alicesk.decapsulate(bobct)

assert alicess == bobss, "Shared secrets do not match!"

print(f"Alice's Shared Secret: [{alicess.hex()}]")
print(f"Bob's   Shared Secret: [{bobss.hex()}]")
```

### 📦 Install
```shell
pip install puantum
```

#### or from source:
```shell
make python
```

### 🥳 Enjoy!
