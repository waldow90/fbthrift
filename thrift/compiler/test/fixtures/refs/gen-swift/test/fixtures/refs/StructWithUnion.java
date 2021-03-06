/**
 * Autogenerated by Thrift
 *
 * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
 *  @generated
 */

package test.fixtures.refs;

import com.facebook.swift.codec.*;
import com.facebook.swift.codec.ThriftField.Requiredness;
import com.facebook.swift.codec.ThriftField.Recursiveness;
import java.util.*;

import static com.google.common.base.MoreObjects.toStringHelper;

@SwiftGenerated
@ThriftStruct(value="StructWithUnion", builder=StructWithUnion.Builder.class)
public final class StructWithUnion {
    @ThriftConstructor
    public StructWithUnion(
        @ThriftField(value=1, name="u", requiredness=Requiredness.NONE) final test.fixtures.refs.MyUnion u,
        @ThriftField(value=2, name="aDouble", requiredness=Requiredness.NONE) final double aDouble,
        @ThriftField(value=3, name="f", requiredness=Requiredness.NONE) final test.fixtures.refs.MyField f
    ) {
        this.u = u;
        this.aDouble = aDouble;
        this.f = f;
    }
    
    @ThriftConstructor
    protected StructWithUnion() {
      this.u = null;
      this.aDouble = 0.;
      this.f = null;
    }
    
    public static class Builder {
        private test.fixtures.refs.MyUnion u;
        @ThriftField(value=1, name="u", requiredness=Requiredness.NONE)
        public Builder setU(test.fixtures.refs.MyUnion u) {
            this.u = u;
            return this;
        }
        private double aDouble;
        @ThriftField(value=2, name="aDouble", requiredness=Requiredness.NONE)
        public Builder setADouble(double aDouble) {
            this.aDouble = aDouble;
            return this;
        }
        private test.fixtures.refs.MyField f;
        @ThriftField(value=3, name="f", requiredness=Requiredness.NONE)
        public Builder setF(test.fixtures.refs.MyField f) {
            this.f = f;
            return this;
        }
    
        public Builder() { }
        public Builder(StructWithUnion other) {
            this.u = other.u;
            this.aDouble = other.aDouble;
            this.f = other.f;
        }
    
        @ThriftConstructor
        public StructWithUnion build() {
            return new StructWithUnion (
                this.u,
                this.aDouble,
                this.f
            );
        }
    }
    
    private final test.fixtures.refs.MyUnion u;
    private final double aDouble;
    private final test.fixtures.refs.MyField f;

    
    @ThriftField(value=1, name="u", requiredness=Requiredness.NONE)
    public test.fixtures.refs.MyUnion getU() { return u; }
        
    @ThriftField(value=2, name="aDouble", requiredness=Requiredness.NONE)
    public double getADouble() { return aDouble; }
        
    @ThriftField(value=3, name="f", requiredness=Requiredness.NONE)
    public test.fixtures.refs.MyField getF() { return f; }
    
    @Override
    public String toString() {
        return toStringHelper(this)
            .add("u", u)
            .add("aDouble", aDouble)
            .add("f", f)
            .toString();
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || getClass() != o.getClass()) {
            return false;
        }
    
        StructWithUnion other = (StructWithUnion)o;
    
        return
            Objects.equals(u, other.u) &&
            Objects.equals(aDouble, other.aDouble) &&
            Objects.equals(f, other.f) &&
            true;
    }
    
    @Override
    public int hashCode() {
        return Arrays.deepHashCode(new Object[] {
            u,
            aDouble,
            f
        });
    }
    
}
