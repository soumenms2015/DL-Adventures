# -*- coding: utf-8 -*-
"""autograd.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/154iBVuHdHNyc-vcYAiSUNDYe-3vst8Bw
"""

class Value:
    """ stores a value and its gradient """

    def __init__(self, data, _children=(), _op=''):
        self.data = data
        self.grad = 0
        # internal variables used for autograd graph construction
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op # the op that produced this node, for graphviz / debugging / etc

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), '+')

        def _backward():
            self.grad += out.grad
            other.grad += out.grad
        out._backward = _backward

        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), '*')

        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
            
            
        out._backward = _backward

        return out
    
    
        
        

    def __pow__(self, other):
        assert isinstance(other, (int, float)), "only supporting int/float powers for now"
        out = Value(self.data**other, (self,), f'**{other}')

        def _backward():
            
            
            self.grad += (other * self.data**(other-1)) * out.grad
        out._backward = _backward

        return out

    def relu(self):
        out = Value(0 if self.data < 0 else self.data, (self,), 'ReLU')

        def _backward():
            self.grad += (out.data > 0) * out.grad
        out._backward = _backward

        return out
    def matmul(self,other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(np.matmul(self.data , other.data), (self, other), 'matmul')
        def _backward():
            self.grad += np.dot(out.grad,other.data.T)
            other.grad += np.dot(self.data.T,out.grad)
            
            
        out._backward = _backward

        return out
    
    def reduce_sum(self,axis = None):
        out = Value(np.sum(self.data,axis = axis), (self,), 'REDUCE_SUM')
        
        def _backward():
            output_shape = np.array(self.data.shape)
            output_shape[axis] = 1
            tile_scaling = self.data.shape // output_shape
            grad = np.reshape(out.grad, output_shape)
            self.grad += np.tile(grad, tile_scaling)
            
        out._backward = _backward

        return out

    def backward(self):

        # topological order all of the children in the graph
        topo = []
        visited = set()
        def build_topo(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)
        build_topo(self)

        # go one variable at a time and apply the chain rule to get its gradient
        self.grad = 1
        for v in reversed(topo):
            #print(v)
            v._backward()

    def __neg__(self): # -self
        return self * -1

    def __radd__(self, other): # other + self
        return self + other

    def __sub__(self, other): # self - other
        return self + (-other)

    def __rsub__(self, other): # other - self
        return other + (-self)

    def __rmul__(self, other): # other * self
        return self * other

    def __truediv__(self, other): # self / other
        return self * other**-1

    def __rtruediv__(self, other): # other / self
        return other * self**-1

    def __repr__(self):
        return f"Value(data={self.data}, grad={self.grad})"

import random
import numpy as np

import random
x_val = []
#generating 100 random data points
for i in range(100):
    a = random.randint(1,10)
    b = random.randint(1,10)
    x_val.append((a,b))
    
x_vals = Value(np.array(x_val))

x_vals

y_true = [1.9*x1 + 2.2*x2 for x1,x2 in x_val]  # w1 and w2 are 1.9 and 2.2 respectively
y_true = np.array([y_true])

y_true = Value(np.transpose(y_true))

y_true

W = Value(np.array([[0.9],[0.2]])) # w1 and w2 initialized to 0.9 and 0.2 respectively
W

epochs = 10
#gradient descent over the whole dataset
for epoch in range(epochs):
    y_pred = x_vals.matmul(W)
    z = (y_true-y_pred)
    z_ = z**2
    out = z_.reduce_sum(axis = 1)
    fin = 0.01*out.reduce_sum()  #(0.01 = 1/100 = BATCH_SIZE)
    fin.backward()
    print(f'loss in epoch {epoch+1} is {fin}')
    W.data = W.data- 0.01*W.grad
    W.grad = 0

W



batch_size = 32
steps = 100
Wb = Value(np.array([[9.0],[22.2]]))# new initialized weights for gradient descent
for step in range(steps):
  ri = np.random.permutation(x_vals.data.shape[0])[:batch_size]
  Xb, yb = Value(x_vals.data[ri]), Value(y_true.data[ri])
  y_predW = Xb.matmul(Wb)
  zb = (yb-y_predW)
  z_b = zb**2
  outb = z_b.reduce_sum(axis = 1)
  finb = 0.32*outb.reduce_sum()  #(0.32 = 1/32 = BATCH_SIZE)
  finb.backward()
  print(f'loss in step {step+1} is {finb}')
  Wb.data = Wb.data- 0.001*Wb.grad
  Wb.grad = 0

Wb





