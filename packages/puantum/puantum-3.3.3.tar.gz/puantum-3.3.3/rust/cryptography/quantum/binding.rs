// IMPORT
use oqs::{kem, sig};
use pyo3;

// MAIN
fn kemalgorithm(name: &str) -> Result<kem::Kem, pyo3::PyErr> {
    let algorithm = match name {
        "BikeL1" => kem::Algorithm::BikeL1,
        "BikeL3" => kem::Algorithm::BikeL3,
        "BikeL5" => kem::Algorithm::BikeL5,
        //
        "ClassicMcEliece348864" => kem::Algorithm::ClassicMcEliece348864,
        "ClassicMcEliece348864f" => kem::Algorithm::ClassicMcEliece348864f,
        "ClassicMcEliece460896" => kem::Algorithm::ClassicMcEliece460896,
        "ClassicMcEliece460896f" => kem::Algorithm::ClassicMcEliece460896f,
        "ClassicMcEliece6688128" => kem::Algorithm::ClassicMcEliece6688128,
        "ClassicMcEliece6688128f" => kem::Algorithm::ClassicMcEliece6688128f,
        "ClassicMcEliece6960119" => kem::Algorithm::ClassicMcEliece6960119,
        "ClassicMcEliece6960119f" => kem::Algorithm::ClassicMcEliece6960119f,
        "ClassicMcEliece8192128" => kem::Algorithm::ClassicMcEliece8192128,
        "ClassicMcEliece8192128f" => kem::Algorithm::ClassicMcEliece8192128f,
        //
        "Hqc128" => kem::Algorithm::Hqc128,
        "Hqc192" => kem::Algorithm::Hqc192,
        "Hqc256" => kem::Algorithm::Hqc256,
        //
        "Kyber512" => kem::Algorithm::Kyber512,
        "Kyber768" => kem::Algorithm::Kyber768,
        "Kyber1024" => kem::Algorithm::Kyber1024,
        //
        "MlKem768" => kem::Algorithm::MlKem768,
        "MlKem512" => kem::Algorithm::MlKem512,
        "MlKem1024" => kem::Algorithm::MlKem1024,
        //
        "NtruPrimeSntrup761" => kem::Algorithm::NtruPrimeSntrup761,
        //
        "FrodoKem1344Aes" => kem::Algorithm::FrodoKem1344Aes,
        "FrodoKem1344Shake" => kem::Algorithm::FrodoKem1344Shake,
        "FrodoKem640Aes" => kem::Algorithm::FrodoKem640Aes,
        "FrodoKem640Shake" => kem::Algorithm::FrodoKem640Shake,
        "FrodoKem976Aes" => kem::Algorithm::FrodoKem976Aes,
        "FrodoKem976Shake" => kem::Algorithm::FrodoKem976Shake,
        _ => return Err(pyo3::exceptions::PyValueError::new_err(format!("Unsupported algorithm: {}", name))),
    };
    let result = kem::Kem::new(algorithm)
        .map_err(|problem| pyo3::exceptions::PyValueError::new_err(format!("Algorithm failure: {}", problem)))?;
    //
    Ok(result)
}

fn sigalgorithm(name: &str) -> Result<sig::Sig, pyo3::PyErr> {
    let algorithm = match name {
        "CrossRsdp128Balanced" => sig::Algorithm::CrossRsdp128Balanced,
        "CrossRsdp128Fast" => sig::Algorithm::CrossRsdp128Fast,
        "CrossRsdp128Small" => sig::Algorithm::CrossRsdp128Small,
        "CrossRsdp192Balanced" => sig::Algorithm::CrossRsdp192Balanced,
        "CrossRsdp192Fast" => sig::Algorithm::CrossRsdp192Fast,
        "CrossRsdp192Small" => sig::Algorithm::CrossRsdp192Small,
        "CrossRsdp256Balanced" => sig::Algorithm::CrossRsdp256Balanced,
        "CrossRsdp256Fast" => sig::Algorithm::CrossRsdp256Fast,
        "CrossRsdp256Small" => sig::Algorithm::CrossRsdp256Small,
        "CrossRsdpg128Balanced" => sig::Algorithm::CrossRsdpg128Balanced,
        "CrossRsdpg128Fast" => sig::Algorithm::CrossRsdpg128Fast,
        "CrossRsdpg128Small" => sig::Algorithm::CrossRsdpg128Small,
        "CrossRsdpg192Balanced" => sig::Algorithm::CrossRsdpg192Balanced,
        "CrossRsdpg192Fast" => sig::Algorithm::CrossRsdpg192Fast,
        "CrossRsdpg192Small" => sig::Algorithm::CrossRsdpg192Small,
        "CrossRsdpg256Balanced" => sig::Algorithm::CrossRsdpg256Balanced,
        "CrossRsdpg256Fast" => sig::Algorithm::CrossRsdpg256Fast,
        "CrossRsdpg256Small" => sig::Algorithm::CrossRsdpg256Small,
        //
        "Dilithium2" => sig::Algorithm::Dilithium2,
        "Dilithium3" => sig::Algorithm::Dilithium3,
        "Dilithium5" => sig::Algorithm::Dilithium5,
        //
        "Falcon512" => sig::Algorithm::Falcon512,
        "Falcon1024" => sig::Algorithm::Falcon1024,
        //
        "Mayo1" => sig::Algorithm::Mayo1,
        "Mayo2" => sig::Algorithm::Mayo2,
        "Mayo3" => sig::Algorithm::Mayo3,
        "Mayo5" => sig::Algorithm::Mayo5,
        //
        "MlDsa44" => sig::Algorithm::MlDsa44,
        "MlDsa65" => sig::Algorithm::MlDsa65,
        "MlDsa87" => sig::Algorithm::MlDsa87,
        //
        "SphincsSha2128fSimple" => sig::Algorithm::SphincsSha2128fSimple,
        "SphincsSha2128sSimple" => sig::Algorithm::SphincsSha2128sSimple,
        "SphincsSha2192fSimple" => sig::Algorithm::SphincsSha2192fSimple,
        "SphincsSha2192sSimple" => sig::Algorithm::SphincsSha2192sSimple,
        "SphincsSha2256fSimple" => sig::Algorithm::SphincsSha2256fSimple,
        "SphincsSha2256sSimple" => sig::Algorithm::SphincsSha2256sSimple,
        "SphincsShake128fSimple" => sig::Algorithm::SphincsShake128fSimple,
        "SphincsShake128sSimple" => sig::Algorithm::SphincsShake128sSimple,
        "SphincsShake192fSimple" => sig::Algorithm::SphincsShake192fSimple,
        "SphincsShake192sSimple" => sig::Algorithm::SphincsShake192sSimple,
        "SphincsShake256fSimple" => sig::Algorithm::SphincsShake256fSimple,
        "SphincsShake256sSimple" => sig::Algorithm::SphincsShake256sSimple,
        //
        "UovOvIII" => sig::Algorithm::UovOvIII,
        "UovOvIIIPkc" => sig::Algorithm::UovOvIIIPkc,
        "UovOvIIIPkcSkc" => sig::Algorithm::UovOvIIIPkcSkc,
        "UovOvIp" => sig::Algorithm::UovOvIp,
        "UovOvIpPkc" => sig::Algorithm::UovOvIpPkc,
        "UovOvIpPkcSkc" => sig::Algorithm::UovOvIpPkcSkc,
        "UovOvIs" => sig::Algorithm::UovOvIs,
        "UovOvIsPkc" => sig::Algorithm::UovOvIsPkc,
        "UovOvIsPkcSkc" => sig::Algorithm::UovOvIsPkcSkc,
        "UovOvV" => sig::Algorithm::UovOvV,
        "UovOvVPkc" => sig::Algorithm::UovOvVPkc,
        "UovOvVPkcSkc" => sig::Algorithm::UovOvVPkcSkc,
        _ => return Err(pyo3::exceptions::PyValueError::new_err(format!("Unsupported algorithm: {}", name))),
    };
    let result = sig::Sig::new(algorithm)
        .map_err(|problem| pyo3::exceptions::PyValueError::new_err(format!("Algorithm failure: {}", problem)))?;
    //
    Ok(result)
}

#[pyo3::pyfunction]
pub fn kemkeygen(name: &str) -> pyo3::PyResult<(Vec<u8>, Vec<u8>)> {
    let algorithm = kemalgorithm(name)?;
    let (publickey, secretkey) = algorithm
        .keypair()
        .map_err(|problem| pyo3::exceptions::PyValueError::new_err(format!("Algorithm failure: {}", problem)))?;
    //
    Ok((secretkey.into_vec(), publickey.into_vec()))
}

#[pyo3::pyfunction]
pub fn kemencapsulate(name: &str, publickey: &[u8]) -> pyo3::PyResult<(Vec<u8>, Vec<u8>)> {
    let algorithm = kemalgorithm(name)?;
    let publickey = algorithm
        .public_key_from_bytes(publickey)
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Invalid PublicKey"))?;
    let (ciphertext, sharedsecret) = algorithm
        .encapsulate(publickey)
        .map_err(|problem| pyo3::exceptions::PyValueError::new_err(format!("Algorithm failure: {}", problem)))?;
    //
    Ok((sharedsecret.into_vec(), ciphertext.into_vec()))
}

#[pyo3::pyfunction]
pub fn kemdecapsulate(name: &str, secretkey: &[u8], ciphertext: &[u8]) -> pyo3::PyResult<Vec<u8>> {
    let algorithm = kemalgorithm(name)?;
    let secretkey = algorithm
        .secret_key_from_bytes(secretkey)
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Invalid SecretKey"))?;
    let ciphertext = algorithm
        .ciphertext_from_bytes(ciphertext)
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Invalid Ciphertext"))?;
    let sharedsecret = algorithm
        .decapsulate(secretkey, ciphertext)
        .map_err(|problem| pyo3::exceptions::PyValueError::new_err(format!("Algorithm failure: {}", problem)))?;
    //
    Ok(sharedsecret.into_vec())
}

#[pyo3::pyfunction]
pub fn sigkeygen(name: &str) -> pyo3::PyResult<(Vec<u8>, Vec<u8>)> {
    let algorithm = sigalgorithm(name)?;
    let (publickey, secretkey) = algorithm
        .keypair()
        .map_err(|problem| pyo3::exceptions::PyValueError::new_err(format!("Algorithm failure: {}", problem)))?;
    //
    Ok((secretkey.into_vec(), publickey.into_vec()))
}

#[pyo3::pyfunction]
pub fn sigsign(name: &str, secretkey: &[u8], message: &[u8]) -> pyo3::PyResult<Vec<u8>> {
    let algorithm = sigalgorithm(name)?;
    let secretkey = algorithm
        .secret_key_from_bytes(secretkey)
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Invalid SecretKey"))?;
    let signature = algorithm.sign(message, secretkey)
        .map_err(|problem| pyo3::exceptions::PyValueError::new_err(format!("Algorithm failure: {}", problem)))?;
    //
    Ok(signature.into_vec())
}

#[pyo3::pyfunction]
pub fn sigverify(name: &str, publickey: &[u8], signature: &[u8], message: &[u8]) -> pyo3::PyResult<bool> {
    let algorithm = sigalgorithm(name)?;
    let publickey = algorithm
        .public_key_from_bytes(publickey)
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Invalid PublicKey"))?;
    let signature = algorithm
        .signature_from_bytes(signature)
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Invalid Signature"))?;
    let valid = algorithm.verify(message, signature, publickey).is_ok();
    //
    Ok(valid)
}
