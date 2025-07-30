package com.example.labexam_02

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }

    fun calculate(view: View) {
        val num1 = findViewById<EditText>(R.id.num1).text.toString().toDoubleOrNull()
        val num2 = findViewById<EditText>(R.id.num2).text.toString().toDoubleOrNull()
        val resultView = findViewById<TextView>(R.id.tvResult)

        if (num1 == null || num2 == null) {
            Toast.makeText(this, "Enter valid numbers", Toast.LENGTH_SHORT).show()
            return
        }

        val result = when (view.id) {
            R.id.btnAdd -> num1 + num2
            R.id.btnSub -> num1 - num2
            R.id.btnMul -> num1 * num2
            R.id.btnDiv -> if (num2 != 0.0) num1 / num2 else {
                Toast.makeText(this, "Cannot divide by zero", Toast.LENGTH_SHORT).show()
                return
            }
            else -> 0.0
        }

        resultView.text = "Result: $result"
    }

}
