# LHE —— Efficient Two-level Homomorphic Encryption in Prime-order Bilinear Groups

Efficient two-level homomorphic encryption 

- Many times add on Enc
- **One-time** mult.  on Enc
- Based on Type 3 (Asymmetric) pairing 
- Combine the lifted-EIGamal encryption scheme  

## Background

Computing on encrypted data.

- Data analysis with taking care of sensitive data

- Homomorphic Encryption (HE)

  - Allows computation on encrypted data

  - Many applications related to privacy-preserving schemes

- Types of HE

  - Additively HE (ex. Okamoto-Uchiyama, Paillier, Lifted-EIgamal)
    $Enc(m)+Enc(m') = Enc(m+m')$
  - Multiplicatively HE (ex. RSA, EIGamal)
    $Enc(m)\times Enc(m') = Enc(mm')$
  - Fully HE (ex. Gentry, BGV, BV, GSW, BFV, ...)
    : Both homomorphic add. and mult.
  

## Pros and Cons

![image-20241217185357088](https://s2.loli.net/2024/12/17/LqbeQjZ7kGzApns.png)





## Our Proposed Two-level HE



Combine lifted-ELGamal with Type 3 pairings

- Level-1 L1 ciphertext CT is same as lifted-EIgamal
- Format of level-2 (L2) CT is same as Freeman's scheme

Note: Type 3 pairings 

- Cyclic groups $\mathbb{G_1},\mathbb{G_2},\mathbb{G_T}$ of the order prime $p$, with bilinear map 
  $$
  e:\mathbb{G_1} \times \mathbb{G_2} \rightarrow \mathbb{G_t}
  $$

- $e(aP,bG) = e(P,Q)^{ab}$ for $a,b \in \mathbb{Z}_p, P \in \mathbb{G_1},\mathbb{G_2}$

- $\mathbb{G_1} \ne \mathbb{G_2}$ and no efficient map from $\mathbb{G_1}$ to $\mathbb{G_2}$



## Setup an Key Generation 

- **Setup**
  - Elliptic curve group $\mathbb{G}_i = \langle P_i \rangle$ with prime order $p$ for $i=1,2$
  - $\mathbb{G}_{\mathrm{T}} = \langle g_{\mathrm{T}} \rangle$, where $g_{\mathrm{T}} = e(P_1, P_2)$
- **Key generation**
  - Secret key $s_1, s_2 \in \mathbb{Z}_p$ is generated at random
  - Public key $s_1P_1, s_2P_2$, and optional precomputation $z_1 = g_{\mathrm{T}}, z_2 = g_{\mathrm{T}}^{s_1}, z_3 = g_{\mathrm{T}}^{s_2}, z_4 = g_{\mathrm{T}}^{s_1s_2}$

So, as it can be related with ECC:

The public part:

- $$
  \begin{cases} \langle P_i \rangle  \\
  \langle g_T \rangle, g_T = e(P_1,P_2) \\ 
  z_1 = g_T , z_2 = g_T^{s_1}, \\ 
  z_3 = g_T^{s_2},z^4 = g_T^{s_1s_2}
  \end{cases}
  $$

- 



## Level- 1 CT and Enc. / Dec. 

- Encrypt:

  - Plaintext  m with randomness r 
  - $\mathrm{Enc}_{\mathbb{G}_i}(m)=(mP_i+rs_iP_i,rP_i)\mathrm{~for~}i=1,2$
  - Duplicated form:
    $\mathrm{Enc}_1(m):=\left(\mathrm{Enc}_{\mathbb{G}_1}(m),\mathrm{Enc}_{\mathbb{G}_2}(m)\right)$

- Decrypt:

  - For $i = 1, 2 $ , decrypt $Enc_{\mathbb{G}_i}(m) = (S,T)$
    by $S - s_iT = (mP_i + rs_iP_i) - s_i (rP_i) = mP_i$,

    to  obtain $m$, solve DL

- Almost same as lifted-EIGamal

    



## Homomorphic addition on L1 CT

-  For $i = 1,2$
  $Enc_{\mathbb{G_i}}(m_1)+Enc_{\mathbb{G_i}}(m_2)$
  $= (m_1P_i+r_1s_iP_i, r_1P_i)+(m_2P_i+r_2s_iP_i,r_2P_i)$
  $= ((m_1+m_2)P_i + (r_1 +r_2)s_iP_i,(r_1+r_2)P_i)$
  $= Enc_{\mathbb{G_1}}(m_1 + m_2)$

- Also,  almost as the same as Lifted-EIGamal 

- Scalar multiplication of ciphertext is easy  
  $nEnc_{\mathbb{G_i}}(m)$
  $= (nm_iP_i+nrs_iP_i,nrP_i)$

  

## One time Homomorphic multiplication

- $$
  \begin{aligned}C_1 \times C_2 &:= (e(S_1,S_2),e(S_1,T_2),e(T_1,S_2),e(T_1,T_2)) \\
  &=(z_1^{m_1m_2}z_4^{\tau\prime},z_2^{\sigma\prime},z_3^{\rho\prime},z_1^{\sigma\prime+\rho\prime-\tau\prime})\in\mathbb{G}_\mathrm{T}^4
  \end{aligned}
  $$

  

- $$
  \begin{aligned}&\bullet C_{1}=(S_{1},T_{1})=(m_{1}P_{1}+r_{1}s_{1}P_{1},r_{1}P_{1})=\mathrm{Enc}_{G_{1}}(m_{1})\in\mathbb{G}_{1}^{2}\\&\bullet C_{2}=(S_{2},T_{2})=(m_{2}P_{2}+r_{2}s_{2}P_{2},r_{2}P_{2})=\mathrm{Enc}_{\mathrm{G}_{2}}(m_{2})\in\mathbb{G}_{2}^{2}\\&\bullet z_1=g_\mathrm{T},z_2=g_\mathrm{T}^{s_1},z_3=g_\mathrm{T}^{s_2},z_4=g_\mathrm{T}^{s_1s_2}\\&\bullet\text{ Tensor product of }C_1,C_2\end{aligned}
  $$

- Its result is level-2 ciphertext





## homomorphic addition on L2  CT

- $$
  \begin{aligned}&\mathrm{Enc}_2(m_1)+\mathrm{Enc}_2(m_2)\\&=(z_1^{m_1}z_4^{\tau_1},z_2^{\sigma_1},z_3^{\rho_1},z_1^{\sigma_1+\rho_1-\tau_1})\\&+(z_1^{m_2}z_4^{\tau_2},z_2^{\sigma_2},z_3^{\rho_2},z_1^{\sigma_2+\rho_2-\tau_2})\\&=(z_1^{m_1+m_2}z_4^{\tau_1+\tau_2},z_2^{\sigma_1+\sigma_2},&z_3^{\rho_1+\rho_2},z_1^{(\sigma_1+\sigma_2)+(\rho_1+\rho_2)-(\tau_1+\tau_2)} )\end{aligned}
  $$

## Decryption for level-2 CT

- Decrypting an level-2 $ciphertext(c_1,c_2,c_3,c_4)$
  $$
  \begin{aligned} 
  \text{Dec}_{2}(c_1,c_2,c_3,c_4) &:= \frac{c_1c_4^{s_1s_2}}{c_2^{s_2}c_3^{s_1}}  \\ 
  &= \frac{e(S_1,S_2)e(s_1T_1,s_2T_2)}{e(S_1,s_2T_2)e(s_1T_1,S_2)} \\ 
  &= e(S_1 - s_1T_1,S_2-s_2T_2) \\ 
  &= e(P_1,P_2)^{mm'}\\
  mm' &= DiscreteLog(e(P_1,P_2),e(P_1,P_2)^{mm'})
  \end{aligned}
  $$
  

![image-20241219214722756](https://s2.loli.net/2024/12/19/5FCzZ8613BJ9t2o.png)



## Confidentiality 

![image-20241219214918583](https://s2.loli.net/2024/12/19/XaoGR6pDPVuYWqU.png)





### IND-CPA Secure under the SXDH assumption 

- Standard security level
- See the proceedings for the proof





### SXDH


$$
\begin{aligned}&P_{1}\in\mathbb{G}_{1},P_{2}\in\mathbb{G}_{2},\text{for random }\alpha,\beta,\gamma,\\&(P_{1},\alpha P_{1},\beta P_{1},\alpha\beta P_{1})\approx(P_{1},\alpha P_{1},\beta P_{1},\gamma P_{1})\mathrm{~and}\\&(P_{2},\alpha P_{2},\beta P_{2},\alpha\beta P_{2})\approx(P_{2},\alpha P_{2},\beta P_{2},\gamma P_{2})\end{aligned}
$$







# Type 3 (Asymmetric) pairing 



#  the lifted-EIGamal encryption scheme











# IND-CPA 安全性和 SXDH 假设

## 1. IND-CPA 安全性

**IND-CPA（可选择明文攻击下的不可区分性）** 是加密方案的一种基础安全性定义。它确保即使攻击者可以选择明文并观察其对应的密文，也无法通过显著高于随机猜测的概率判断密文对应的明文。

### 定义：

一个加密方案 $ \Pi = (\text{KeyGen}, \text{Encrypt}, \text{Decrypt}) $ 是 **IND-CPA 安全** 的，如果没有多项式时间内的攻击者 $ \mathcal{A} $ 能通过以下游戏以显著优于 $ \frac{1}{2} $ 的概率获胜：

1. **密钥生成**:  
   挑战者生成公私钥对 $ (pk, sk) \gets \text{KeyGen}() $。

2. **消息提交**:  
   攻击者 $ \mathcal{A} $ 提交两个等长的明文 $ m_0 $ 和 $ m_1 $ 给挑战者。

3. **挑战密文**:  
   挑战者随机选择一个比特 $ b \in \{0,1\} $，并返回密文 $ c^* = \text{Encrypt}(pk, m_b) $ 给攻击者。

4. **攻击者猜测**:  
   攻击者输出猜测 $ b' \in \{0,1\} $ 以判断 $ b $ 的值。

攻击者的优势定义为：
$$
\text{Adv}_{\mathcal{A}}^{\text{IND-CPA}} = \left| \Pr[b' = b] - \frac{1}{2} \right|。
$$

如果 $ \text{Adv}_{\mathcal{A}}^{\text{IND-CPA}} $ 是可忽略的（即任何多项式分量都比它大），那么方案 $ \Pi $ 被认为是 **IND-CPA 安全** 的。

### 核心思想：

即使攻击者可以访问明文及其对应的密文，也无法从密文中推断任何与明文相关的有意义信息。

---

## 2. SXDH 假设

**SXDH（对称外部 Diffie-Hellman 假设）** 是双线性配对环境中的一种计算难题假设，推广自经典的 Diffie-Hellman 假设。

### 双线性配对场景：

考虑一个双线性配对：
$$
e : G_1 \times G_2 \to G_T,
$$
其中：

- $ G_1 $、$ G_2 $ 是阶为素数 $ p $ 的两个不同群，

- $ G_T $ 是相同阶数 $ p $ 的目标群，

- 配对 $ e $ 满足双线性性质：
  $$
  e(g_1^a, g_2^b) = e(g_1, g_2)^{ab}, \quad \forall g_1 \in G_1, g_2 \in G_2, a, b \in \mathbb{Z}_p。
  $$

### 假设：

**SXDH 假设** 认为在 $ G_1 $ 和 $ G_2 $ 中，决定性 Diffie-Hellman（Decisional Diffie-Hellman, DDH）问题是困难的。也就是说，给定随机群元素：
$$
(g, g^a, g^b, g^c) \in G_1 \quad \text{或} \quad G_2，
$$
计算 $ c = ab \mod p $ 是计算上不可行的。

### 形式化：

对于 $ G_1 $：
$$
\text{给定 } (g, g^a, g^b, g^c) \in G_1，\text{判断 } c = ab。
$$
对于 $ G_2 $：
$$
\text{给定 } (h, h^a, h^b, h^c) \in G_2，\text{判断 } c = ab。
$$

如果攻击者无法区分 $ (g, g^a, g^b, g^{ab}) $ 和 $ (g, g^a, g^b, g^{r}) $（其中 $ r $ 是随机值）的分布，则 DDH 是困难的，SXDH 假设成立。

# Type 3 (Asymmetric) pairing 

# 什么是抽象代数中的 Type 3（非对称）配对？

在抽象代数中，尤其是密码学配对的上下文中，**Type 3 配对（非对称配对）** 指的是一种特定的双线性映射，通常用于基于配对的密码学。这种配对是非对称的，因为它涉及两个不同的源群，而不是一个相同的群。以下是详细的解释：

---

## **配对的定义**

配对是一种双线性映射 $e$，它满足以下属性：
$$
e: G_1 \times G_2 \to G_T
$$
其中：
- $G_1$ 和 $G_2$ 是两个阶为素数 $p$ 的循环群，
- $G_T$ 是另一个相同阶 $p$ 的循环群，
- $e$ 满足双线性性、非退化性和可有效计算性：
  1. **双线性性**：对于所有 $g_1 \in G_1, g_2 \in G_2, a, b \in \mathbb{Z}_p$，有：
     $$
     e(g_1^a, g_2^b) = e(g_1, g_2)^{ab}.
     $$
  2. **非退化性**：存在 $g_1 \in G_1, g_2 \in G_2$，使得 $e(g_1, g_2) \neq 1$。
  3. **可有效计算性**：存在一个高效的算法可以计算 $e(g_1, g_2)$。

---

## **配对的类型**

根据 $G_1$ 和 $G_2$ 之间的关系，配对分为三种主要类型：

1. **Type 1（对称配对）：**  
   在这种情况下，$G_1 = G_2$。即配对作用于同一个群：
   $$
   e: G_1 \times G_1 \to G_T.
   $$

   - **优点**：结构简单，易于实现。
   - **缺点**：在实际应用中效率往往较低。

2. **Type 2（部分非对称配对）：**  
   在这种情况下，$G_1 \neq G_2$，但存在一个可高效计算的同构 $\phi: G_2 \to G_1$。  
   配对定义为：
   $$
   e: G_1 \times G_2 \to G_T.
   $$

   - **优点**：相比 Type 1 提供了更多的灵活性。
   - **缺点**：同构 $\phi$ 有时会限制效率。

3. **Type 3（非对称配对）：**  
   在这种情况下，$G_1 \neq G_2$，且 $G_1$ 和 $G_2$ 之间不存在一个可高效计算的同构。  
   配对定义为：
   $$
   e: G_1 \times G_2 \to G_T.
   $$

   - **关键属性**：$G_1$ 和 $G_2$ 是两个独立的群，其结构在计算上彼此无关。
   - **优点**：比 Type 2 配对效率更高，因为不需要同构运算，从而加快计算速度。
   - **缺点**：相比 Type 1 配对，构造更为复杂。

---

## **从抽象代数的角度理解**

从抽象代数的角度来看，Type 3 配对包含以下组件：
1. $G_1$ 和 $G_2$ 是两个不同的加法群或乘法群，通常是椭圆曲线群，且它们的阶均为素数 $p$。
2. $G_T$ 通常是有限域（例如 $\mathbb{F}_{p^k}^*$）的子群，其中 $k$ 是嵌入度，与安全参数相关。

这些群被选择使得：
- 在 $G_1$、$G_2$ 和 $G_T$ 中，离散对数问题（DLP）是计算困难的。
- 双线性映射 $e$ 满足双线性性、非退化性和可有效计算性。

---

## **为什么 Type 3 配对有用**

1. **密码学效率：**  
   Type 3 配对避免了同构的开销，使其在实际应用中更加高效，例如：
   - 基于身份的加密（IBE），
   - 基于属性的加密（ABE），
   - 短签名方案，
   - 零知识证明。

2. **安全性：**  
   通过区分 $G_1$ 和 $G_2$，Type 3 配对为攻击者尝试解决密码学问题（例如离散对数问题或配对反演问题）增加了复杂性。

3. **可扩展性：**  
   Type 3 配对通常允许使用较小的域，从而在不降低安全性的情况下提高性能。

---

## **Type 3 配对的一个例子**

考虑以下情况：
- $G_1$ 是有限域 $\mathbb{F}_p$ 上椭圆曲线 $E_1$ 上点的群，
- $G_2$ 是 $E_1$ 的一个 *twist*（扩展域 $\mathbb{F}_{p^k}$ 上的曲线）上的点的群，
- $G_T$ 是乘法群 $\mathbb{F}_{p^k}^*$ 的一个子群。

配对 $e$ 的映射为：
$$
e: G_1 \times G_2 \to G_T.
$$

这样的结构通常用于密码学库（如 PBC：基于配对的密码学）以及协议（如 BLS 签名和 zk-SNARKs）。

---

## **总结**

**Type 3 配对** 是一种非对称的双线性映射 $e: G_1 \times G_2 \to G_T$，其中 $G_1$ 和 $G_2$ 之间不存在可高效计算的同构。这种配对通过利用不同的群，提供了高效且安全的基础，用于许多高级的密码学协议。



# the lifted-EIGamal encryption scheme

# 什么是 Lifted-ElGamal 加密方案？

**Lifted-ElGamal 加密方案** 是经典 **ElGamal 加密方案** 的扩展形式，通常应用于更复杂的密码学场景，例如同态加密和基于配对的加密。在这种扩展方案中，ElGamal 的加密结构被提升到支持更多操作的数学结构中，例如在双线性配对的上下文中。

---

## **ElGamal 加密的基本形式**

经典 ElGamal 加密方案定义在一个循环群 $G$ 上，该群的阶为素数 $p$。该方案的安全性基于离散对数问题的难解性。

1. **参数设置**:  
   - 选择一个循环群 $G$，其阶为素数 $p$。
   - 选择生成元 $g \in G$。

2. **密钥生成**:  
   - 随机选择一个私钥 $x \in \mathbb{Z}_p$。
   - 计算公钥 $h = g^x$。
   - 公钥为 $(G, p, g, h)$，私钥为 $x$。

3. **加密过程**:  
   给定消息 $m \in G$ 和随机值 $r \in \mathbb{Z}_p$：
   $$
   c = (c_1, c_2) = (g^r, h^r \cdot m)。
   $$

4. **解密过程**:  
   给定密文 $c = (c_1, c_2)$ 和私钥 $x$，恢复消息 $m$：
   $$
   m = c_2 \cdot (c_1^x)^{-1}。
   $$

---

## **Lifted-ElGamal 加密方案**

Lifted-ElGamal 加密方案扩展了 ElGamal 的结构，使其适用于双线性配对环境中的群。这种扩展特别适用于需要额外结构的加密操作，如同态操作。

### **1. 双线性配对环境**

Lifted-ElGamal 工作在一个双线性配对的数学环境中：
$$
e: G_1 \times G_2 \to G_T，
$$
其中：
- $G_1$ 和 $G_2$ 是两个阶为素数 $p$ 的循环群，
- $G_T$ 是另一个相同阶的循环群，
- $e$ 是一个双线性映射，满足：
  $$
  e(g_1^a, g_2^b) = e(g_1, g_2)^{ab}, \quad \forall g_1 \in G_1, g_2 \in G_2, a, b \in \mathbb{Z}_p。
  $$

### **2. 参数设置**

- 选择两个循环群 $G_1$ 和 $G_2$，它们的阶均为素数 $p$。
- 选择生成元 $P \in G_1$ 和 $Q \in G_2$。

### **3. 密钥生成**

- 私钥：随机选择 $x \in \mathbb{Z}_p$。
- 公钥：计算 $H = xQ$（其中 $Q \in G_2$）。
- 公钥为 $(P, Q, H)$，私钥为 $x$。

### **4. 加密过程**

给定消息 $m \in G_T$，选择随机值 $r \in \mathbb{Z}_p$，密文为：
$$
C = (C_1, C_2) = (rP, e(P, H)^r \cdot m)。
$$
其中：
- $C_1 = rP \in G_1$，
- $C_2 = e(P, H)^r \cdot m \in G_T$。

### **5. 解密过程**

给定密文 $C = (C_1, C_2)$ 和私钥 $x$，通过以下步骤恢复消息 $m$：
1. 计算 $e(C_1, xQ)$：
   $$
   e(C_1, xQ) = e(rP, xQ) = e(P, Q)^{xr}。
   $$
2. 使用 $C_2$ 解密：
   $$
   m = C_2 \cdot (e(C_1, xQ))^{-1}。
   $$

---

## **Lifted-ElGamal 的特性**

1. **同态加密特性**:  
   Lifted-ElGamal 具有加法同态特性，这意味着对两个密文对应的明文加法可以通过操作密文直接完成。

   - 给定两个密文：
     $$
     C_1 = (r_1P, e(P, H)^{r_1} \cdot m_1)，
     $$
     $$
     C_2 = (r_2P, e(P, H)^{r_2} \cdot m_2)，
     $$
     两者的加法操作结果为：
     $$
     C = (C_1 + C_2) = ((r_1 + r_2)P, e(P, H)^{r_1 + r_2} \cdot (m_1 \cdot m_2))。
     $$

2. **安全性**:  
   Lifted-ElGamal 的安全性基于 **双线性 Diffie-Hellman 假设（BDH）**。这意味着在双线性配对环境下，离散对数问题和相关问题是计算困难的。

3. **效率**:  
   与经典 ElGamal 相比，Lifted-ElGamal 增加了对双线性映射的依赖，因此需要更多计算资源，但同时支持更复杂的操作，如在 $G_T$ 中进行运算。

---

## **应用场景**

Lifted-ElGamal 加密方案广泛应用于以下领域：
1. **多方计算（MPC）**:  
   由于其同态特性，Lifted-ElGamal 可用于多方安全计算协议。
2. **属性基加密（ABE）**:  
   作为底层加密机制，支持复杂的访问控制策略。
3. **同态签名**:  
   允许在密文上验证消息相关属性。
4. **双线性配对加密**:  
   被用于许多基于配对的密码系统。

---

## **总结**

Lifted-ElGamal 是经典 ElGamal 的扩展形式，适用于双线性配对环境，能够支持复杂的同态操作。其主要特性包括：
- 继承了 ElGamal 的随机性和安全性，
- 通过双线性映射支持更复杂的操作，
- 应用于多方计算和基于属性的加密等高级密码学场景。

其安全性和功能性使其成为现代密码学中重要的构建块之一。

